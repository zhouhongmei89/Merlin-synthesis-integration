using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Tts.Offline;
using Microsoft.Tts.Offline.Htk;
using System.IO;
using System.Xml;

namespace ConvertFormatDecode
{
    class Program
    {
        static void Main(string[] args)
        {
            try
            {
                string configPath = args[0];
                XmlDocument doc = new XmlDocument();
                doc.Load(configPath);
                XmlNode xn = doc.SelectSingleNode("Settings");
                //Convertformat
                XmlElement labInConvertEl = (XmlElement)xn.SelectSingleNode("ConvertFormat/LabInput");
                string labInConvert = labInConvertEl.InnerText;

                XmlElement f0LabInConvertEl = (XmlElement)xn.SelectSingleNode("ConvertFormat/F0LabInput");
                string f0LabInConvert = f0LabInConvertEl.InnerText;

                XmlElement labOutConvertEl = (XmlElement)xn.SelectSingleNode("ConvertFormat/LabOutput");
                string labOutConvert = labOutConvertEl.InnerText;

                XmlElement f0LabOutConvertEl = (XmlElement)xn.SelectSingleNode("ConvertFormat/f0LabOutput");
                string f0LabOutConvert = f0LabOutConvertEl.InnerText;

                if (!Directory.Exists(labOutConvert))
                {
                    Directory.CreateDirectory(labOutConvert);
                }

                if (!Directory.Exists(f0LabOutConvert))
                {
                    Directory.CreateDirectory(f0LabOutConvert);
                }

                XmlElement CmpOutCEl = (XmlElement)xn.SelectSingleNode("ConvertFormat/CmpOutC");
                string CmpOutC = CmpOutCEl.InnerText;
                if (!Directory.Exists(CmpOutC))
                {
                    Directory.CreateDirectory(CmpOutC);
                }

                //decode
                XmlElement ConfigDirEl = (XmlElement)xn.SelectSingleNode("Decode/ConfigDir");
                string ConfigDir = ConfigDirEl.InnerText;

                XmlElement ModelDirEl = (XmlElement)xn.SelectSingleNode("Decode/ModelDir");
                string ModelDir = ModelDirEl.InnerText;

                XmlElement ModelNameEl = (XmlElement)xn.SelectSingleNode("Decode/ModelName");
                string ModelName = ModelNameEl.InnerText;

                XmlElement InDimEl = (XmlElement)xn.SelectSingleNode("Decode/InDim");
                int inDim = Convert.ToInt32(InDimEl.InnerText);

                XmlElement outDimEl = (XmlElement)xn.SelectSingleNode("Decode/OutDim");
                int outDim = Convert.ToInt32(outDimEl.InnerText);

                XmlElement f0DimEl = (XmlElement)xn.SelectSingleNode("Decode/F0Dim");
                int f0Dim = Convert.ToInt32(f0DimEl.InnerText);

                XmlElement CNTKPathEl = (XmlElement)xn.SelectSingleNode("Decode/CNTKPath");
                string CNTKPath = CNTKPathEl.InnerText;

                XmlElement ConfigFileEl = (XmlElement)xn.SelectSingleNode("Decode/ConfigFile");
                string ConfigFile = ConfigFileEl.InnerText;

                XmlElement decodeWithF0 = (XmlElement)xn.SelectSingleNode("Decode/WithF0");
                bool isDecodeWithF0 = Convert.ToBoolean(decodeWithF0.InnerText);

                //file list
                //XmlElement LabInFilelistEl = (XmlElement)xn.SelectSingleNode("FileList/LabInput");
                //string LabInFilelist = LabInFilelistEl.InnerText;

                XmlElement ScpPathEl = (XmlElement)xn.SelectSingleNode("FileList/ScpPath");
                string ScpPath = ScpPathEl.InnerText;

                XmlElement filelistEl = (XmlElement)xn.SelectSingleNode("FileList/FileListFile");
                string FileListFile = filelistEl.InnerText;

                if (!Directory.Exists(ScpPath))
                {
                    Directory.CreateDirectory(ScpPath);
                }

                //Convertcmp
                XmlElement CmpOutPathEl = (XmlElement)xn.SelectSingleNode("ConvertCMP/CmpOutPath");
                string CmpOutPath = CmpOutPathEl.InnerText;
                if (!Directory.Exists(CmpOutPath))
                {
                    Directory.CreateDirectory(CmpOutPath);
                }

                Console.WriteLine("Start Convert Merlin lab to CNTK lab");
                convertMerlinData(labInConvert, labOutConvert, inDim);
                if (isDecodeWithF0)
                {
                    convertMerlinData(f0LabInConvert, f0LabOutConvert, f0Dim);
                }

                Console.WriteLine("Start get scp file");
                prepareFilelist(labOutConvert, CmpOutC, ScpPath, FileListFile, f0LabOutConvert, isDecodeWithF0);
                Console.WriteLine("Start decode");

                ExcuteCNTK(CNTKPath, ConfigDir, ModelDir, ModelName, inDim, outDim, Path.Combine(ScpPath, @"lab.scp"), Path.Combine(ScpPath, @"cmp.scp"), ConfigFile, isDecodeWithF0, Path.Combine(ScpPath, @"f0.scp"), f0Dim);
                Console.WriteLine("Start Convert CNTK cmp to Merlin cmp");
                ConvertTestCMP(Path.Combine(ScpPath, @"cmp.scp"), CmpOutPath, outDim);
            }
            catch(Exception e)
            {
                Console.WriteLine(e.Message);
            }
        }

        private static void convertMerlinData(string inputlab,string outputlab, int dim)
        {
            try
            {
                DirectoryInfo labDir = new DirectoryInfo(inputlab);
                FileInfo[] labfiles = labDir.GetFiles();


                foreach (FileInfo fi in labfiles)
                {
                    convertFloatBinaryToHTK(Path.Combine(labDir.ToString(), fi.Name), dim, Path.Combine(outputlab, fi.Name));
                }

            }
            catch(Exception e)
            {
                Console.WriteLine("convertMerlinData Error : " + e.Message);
            }
            
         
        }

        private static void ConvertTestCMP(string inputPath, string outputPath, int dim)
        {

            try
            {
                if (!Directory.Exists(outputPath))
                {
                    Directory.CreateDirectory(outputPath);
                }
                var lines = File.ReadLines(inputPath);
                foreach (string line in lines)
                {
                    string fileName = Path.GetFileName(line);
                    string floatbinary = Path.Combine(outputPath, fileName);
                    convertHTKToFloatBinary(floatbinary, dim, line);
                }
            }
            catch(Exception e)
            {
                Console.WriteLine("ConvertTestCMP error:" + e.Message);
            }
            

        }

        private static void convertHTKToFloatBinary(string binaryFile, int dim, string htkFile)
        {
            try
            {
                HtkParameterFile htkParameterFile = new HtkParameterFile();
                htkParameterFile.BigEndianLoad(htkFile);

                FileStream fs = new FileStream(binaryFile, FileMode.Create); //初始化FileStream对象
                BinaryWriter bw = new BinaryWriter(fs); //创建BinaryWriter对象
                                                        //写入文件
                for (int i = 0; i < htkParameterFile.Data.Length; i++)
                {
                    for (int j = 0; j < htkParameterFile.Data[i].Length; j++)
                    {
                        bw.Write(htkParameterFile.Data[i][j]);
                    }
                }
                bw.Close(); //关闭BinaryWriter对象
                fs.Close(); //关闭文件流

            }
            catch(Exception e)
            {
                Console.WriteLine("convertHTKToFloatBinary Error:" + e.Message);
            }
            
        }
        private static void prepareFilelist(string labpath, string cmppath,string outputPath,string filelistpath, string f0labpath, bool isDecodeWithF0)
        {
            try
            {
                List<string> filelist = new List<string>();
                using (StreamReader sr = new StreamReader(filelistpath))
                {
                    string line = "";
                    do
                    {
                        line = sr.ReadLine();
                        if (line == "" || line == null)
                            break;
                        line = line.Trim();
                        filelist.Add(line);
                    } while (line!=null||line!="");
                    
                }
                //DirectoryInfo labDir = new DirectoryInfo(labpath);
                //FileInfo[] labfiles = labDir.GetFiles();
                
                if (!Directory.Exists(cmppath))
                {
                    Directory.CreateDirectory(cmppath);
                }

                if (!Directory.Exists(outputPath))
                {
                    Directory.CreateDirectory(outputPath);
                }

                using (StreamWriter writer = new StreamWriter(Path.Combine(outputPath, @"lab.scp")))
                {
                    using (StreamWriter writer2 = new StreamWriter(Path.Combine(outputPath, @"cmp.scp")))
                    {
                        foreach (string fi in filelist)
                        {
                            // string filename = Path.GetFileNameWithoutExtension(Path.Combine(labDir.ToString(), fi));
                            writer.WriteLine(Path.Combine(labpath, fi + ".lab"));
                            writer2.WriteLine(Path.Combine(cmppath, fi + ".cmp"));

                        }
                    }
                }
                if (isDecodeWithF0)
                {
                    using (StreamWriter writer = new StreamWriter(Path.Combine(outputPath, @"f0.scp")))
                    {
                        foreach (string fi in filelist)
                        {
                            // string filename = Path.GetFileNameWithoutExtension(Path.Combine(labDir.ToString(), fi));
                            writer.WriteLine(Path.Combine(f0labpath, fi + ".lab"));

                        }
                    }
                }

            }
            catch (Exception e)
            {
                Console.WriteLine("prepareFilelist Error: " + e.Message);
            }
            
        }

        private static void ExcuteCNTK(string cntkPath,string ConfigDir,string ModelDir, string ModelName, int inDim, int OutDim, string TestInScpFile, string TestOutScpFile, string ConfigFile, bool isDecodeWithF0, string TestF0InScpFile, int F0Dim)
        {
            try {
                string[] devices = cntkPath.Split('\\');
                string device = devices[0];

                string cmdStr = string.Empty;
                if (isDecodeWithF0)
                {
                    cmdStr = cntkPath + @"  ConfigDir=" + ConfigDir + "  ModelDir=" + ModelDir + "  ModelName=" + ModelName + " InDim=" + inDim + " OutDim=" + OutDim + "  TestInScpFile=" + TestInScpFile + "  TestOutScpFile=" + TestOutScpFile + "  ConfigFile=" + ConfigFile + " TestF0InScpFile=" + TestF0InScpFile + " F0Dim=" + F0Dim;
                }
                else
                {
                    cmdStr = cntkPath + @"  ConfigDir=" + ConfigDir + "  ModelDir=" + ModelDir + "  ModelName=" + ModelName + " InDim=" + inDim + " OutDim=" + OutDim + "  TestInScpFile=" + TestInScpFile + "  TestOutScpFile=" + TestOutScpFile + "  ConfigFile=" + ConfigFile;
                }
                System.Diagnostics.Process exep = new System.Diagnostics.Process();
                exep.StartInfo.FileName = @"cmd.exe";
                //exep.StartInfo.Arguments = cmdStr;
                exep.StartInfo.CreateNoWindow = false;
                exep.StartInfo.UseShellExecute = false;
                exep.StartInfo.RedirectStandardInput = true;
                exep.StartInfo.RedirectStandardOutput = true;
                exep.Start();
                //exep.StandardInput.WriteLine(device);
                //exep.StandardInput.WriteLine("cd " + cntkPath);
                exep.StandardInput.WriteLine(cmdStr + "&exit");
                //exep.StandardInput.WriteLine("exit");
                exep.StandardInput.AutoFlush = true;
                //get output message
                string stroutput = exep.StandardOutput.ReadToEnd();
                exep.WaitForExit();
                exep.Close();
                Console.WriteLine(stroutput);
                Console.WriteLine("finish");
            }
            catch(Exception e)
            {
                Console.WriteLine("ExcuteCNTK Error : " + e.Message);
            }            
        }

        private static void convertFloatBinaryToHTK(string binaryFile, int dim, string htkFile)
        {
            try
            {
                List<float> data = new List<float>();
                using (BinaryReader binary = new BinaryReader(File.Open(binaryFile, FileMode.Open)))
                {
                    try
                    {
                        while (true)
                        {
                            float x = binary.ReadSingle();
                            data.Add(x);
                        }
                    }
                    catch (EndOfStreamException e)
                    {
                        Console.WriteLine(e.Message);
                        Console.WriteLine("to the end");
                    }
                }

                if (data.Count % dim != 0)
                {
                    Console.WriteLine("error!");
                    return;
                }

                int frames = data.Count / dim;
                HtkParameterFile htkParameterFile = new HtkParameterFile();
                htkParameterFile.SamplePeriodInSecond = 0.001f * 5;
                htkParameterFile.ParameterKind = ParameterKinds.UserDefined;
                htkParameterFile.Data = new float[frames][];
                for (int i = 0; i < frames; i++)
                {
                    htkParameterFile.Data[i] = new float[dim];
                    for (int j = 0; j < dim; j++)
                    {
                        htkParameterFile.Data[i][j] = data[i * dim + j];
                    }
                }
                htkParameterFile.Save(htkFile);
            }
            catch(Exception e)
            {
                Console.WriteLine("convertFloatBinaryToHTK Error: " + e.Message);
            }

        }

    }
}
