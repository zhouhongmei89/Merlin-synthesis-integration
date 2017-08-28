using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Text.RegularExpressions;
using System.Xml;

namespace merlinstatalign
{
    class Program
    {
       static List<int> modifydexlist = new List<int>();
        static void Main(string[] args)
        {
            try
            {
                string configPath = args[0];
                XmlDocument doc = new XmlDocument();
                doc.Load(configPath);
                XmlNode xn = doc.SelectSingleNode("Settings");
                XmlNodeList xnl = xn.ChildNodes;
                XmlElement phoneNode = (XmlElement)xn.SelectSingleNode("PhoneFile");
                XmlElement outputNode = (XmlElement)xn.SelectSingleNode("OutputDirectory");
                XmlElement TextFilePathNode = (XmlElement)xn.SelectSingleNode("TextFilePath");

                string phoneAlignDir = phoneNode.InnerText;
                string outputpath = outputNode.InnerText;

                if (Directory.Exists(outputpath))
                {
                    Directory.Delete(outputpath, true);
                }

                //string offline = Path.Combine(System.AppDomain.CurrentDomain.SetupInformation.ApplicationBase, "offline");
                string offline = @"C:\work\offline_0801";
                Console.WriteLine(offline);
                ExcuteFullcontextlable(configPath, offline);

                using (StreamReader TEXT = new StreamReader(TextFilePathNode.InnerText))
                {
                    string line = string.Empty;
                    while ((line = TEXT.ReadLine()) != null)
                    {
                        string[] lineInfo = line.Split(' ');
                        string fileId = lineInfo[0];
                        string phonefile = Path.Combine(phoneAlignDir, fileId + ".txt");
                        if (File.Exists(phonefile))
                        {
                            string statefile = Path.Combine(outputpath, "state", fileId + ".lab");
                            string silAlignDir = Path.Combine(outputpath, "silAlign");
                            if (!Directory.Exists(silAlignDir))
                            {
                                Directory.CreateDirectory(silAlignDir);
                            }
                            string outputDir = Path.Combine(outputpath, "output");
                            if (!Directory.Exists(outputDir))
                            {
                                Directory.CreateDirectory(outputDir);
                            }
                            modifyStatefile(statefile, phonefile, Path.Combine(silAlignDir, fileId + ".lab"));
                            modifyphonename(phonefile, Path.Combine(silAlignDir, fileId + ".lab"), Path.Combine(outputDir, fileId + ".lab"));
                        }
                    }
                }

            }
            catch(Exception e)
            {
                Console.WriteLine(e.Message);
            }           

        }

        private static void ExcuteFullcontextlable(string configPath,string offlinePath)
        {
            try
            {
                string[] devices = offlinePath.Split('\\');
                string device = devices[0];
                string cmdStr = @"FullContextLabelGenerator.exe" + @" -config " + configPath;
                System.Diagnostics.Process exep = new System.Diagnostics.Process();
                exep.StartInfo.FileName = @"cmd.exe";
                //exep.StartInfo.Arguments = cmdStr;
                exep.StartInfo.CreateNoWindow = false;
                exep.StartInfo.UseShellExecute = false;
                exep.StartInfo.RedirectStandardInput = true;
                exep.StartInfo.RedirectStandardOutput = true;
                exep.Start();
                exep.StandardInput.WriteLine(device);
                exep.StandardInput.WriteLine("cd " + offlinePath);
                exep.StandardInput.WriteLine(cmdStr + "&exit");
                exep.StandardInput.AutoFlush = true;
                //get output message
                string strOuput = exep.StandardOutput.ReadToEnd();
                exep.WaitForExit();
                exep.Close();
                Console.WriteLine(strOuput);
                Console.WriteLine("finish");
            }
            catch(Exception e)
            {
                    Console.WriteLine(e.Message);
                
            }
              

        }
        private static void modifyStatefile(string statefile,string phonefile,string outputfile)
        {
            //try
            //{
                //align sil
                Dictionary<int, string> phoneDic = new Dictionary<int, string>();
                Dictionary<int, string> labDic = new Dictionary<int, string>();
                List<string> labDicsingle = new List<string>();
                List<string> tempsingle = new List<string>();
                List<int> sildex = new List<int>();
                List<string> labstring = new List<string>();
                List<string> siladdlist = new List<string>();
                List<string> resultLab = new List<string>();

                string[] phoneArray = File.ReadAllLines(phonefile);
                string[] lablines = File.ReadAllLines(statefile);

               // int a = (int)Math.Round((lablines.Count() * 1.0)/phoneArray.Count(), 0);
               //if (Math.Round(phoneArray.Count()/(lablines.Count()*1.0),0)!=5.0)
               // {
               //     Console.WriteLine("state and phone number is not match");
               //     return;
               // }

                for (int i = 0; i < lablines.Length; i++)
                {
                    labstring.Add(lablines[i]);

                    //get phone between-and+
                    string[] line = lablines[i].Split(' ');
                    string value = Regex.Match(line[2], @"(?<=\-)\w+(?=\+)", RegexOptions.IgnoreCase).Value;

                    labDic[i] = value;

                    if (i < 5)
                        siladdlist.Add(lablines[i]);

                }

                //get single phone from lab
                for (int i = 0; i < labDic.Count; i = i + 5)
                {
                    tempsingle.Add(labDic[i]);
                    labDicsingle.Add(labDic[i]);
                }
                for (int j = 0; j < phoneArray.Length; j++)
                {
                    string[] line = phoneArray[j].Split(' ');
                    phoneDic[j] = line[1];
                }

            //debug delete sil

            //for (int i = 0; i < tempsingle.Count; i++)
            //{
            //    if (tempsingle[i].ToLower() == "sil")
            //    {
            //        tempsingle.RemoveAt(i);
            //        if (i == tempsingle.Count)
            //            continue;
            //        if (tempsingle[i].ToLower() == "sil")
            //            tempsingle.RemoveAt(i);
            //    }

            //}

            //List<string> phonearrary = new List<string>();
            //for (int i = 0; i < phoneDic.Count; i++)
            //{
            //    phonearrary.Add(phoneDic[i]);
            //}

            //for (int i = 0; i < phonearrary.Count; i++)
            //{
            //    if (phonearrary[i].ToLower() == "sil")
            //    {
            //        phonearrary.RemoveAt(i);
            //        if (i == phonearrary.Count)
            //            continue;
            //        if (phonearrary[i].ToLower() == "sil")
            //            phonearrary.RemoveAt(i);
            //    }
            //}



            //set add sil 1,set delete sil 0
            int deletedex = 0;

                for (int i = 0; i < phoneDic.Count; i++)
                {
                    if (phoneDic[i].ToLower() == tempsingle[i].ToLower())
                        continue;
                    else
                    {
                        if (phoneDic[i].ToLower() == "sil")
                        {
                            labDicsingle.Insert(i+ deletedex, "1");
                            tempsingle.Insert(i, "1");   //set need add sil value "1"  
                            modifydexlist.Add(i);
                           
                            


                        }
                        else if (tempsingle[i].ToLower() == "sil")
                        {                          
                            labDicsingle[i + deletedex] = "0";
                            tempsingle.RemoveAt(i);
                            deletedex++;
                            if(tempsingle[i].ToLower() == "sil")
                            {
                                labDicsingle[i+ deletedex] = "0";
                                tempsingle.RemoveAt(i);
                                deletedex++;
                            }
                            modifydexlist.Add(i);
                            
                            
                        }

                    }
                }
                if (phoneDic.Count < tempsingle.Count)
                {
                    for (int j = phoneDic.Count; j < labDicsingle.Count; j++)
                    {
                        if (labDicsingle[j].ToLower() == "sil")
                        {
                            labDicsingle[j] = "0";
                        }
                    }


                }

                //value=0,delete sil,=1 add sil 
                int decount = 0;
                for (int i = 0; i < labDicsingle.Count; i++)
                {
                    if (labDicsingle[i] == "1")
                    {

                        labstring.Insert((i-decount) * 5, siladdlist[0]);
                        labstring.Insert((i-decount) * 5 + 1, siladdlist[1]);
                        labstring.Insert((i-decount) * 5 + 2, siladdlist[2]);
                        labstring.Insert((i-decount) * 5 + 3, siladdlist[3]);
                        labstring.Insert((i-decount) * 5 + 4, siladdlist[4]);
                    }
                    else if (labDicsingle[i] == "0")
                    {
                        labstring.RemoveAt((i - decount) * 5);
                        labstring.RemoveAt((i - decount) * 5);
                        labstring.RemoveAt((i - decount) * 5);
                        labstring.RemoveAt((i - decount) * 5);
                        labstring.RemoveAt((i - decount) * 5);
                        decount++;

                    }

                }

                //string path = Path.GetDirectoryName(labnewFile);
                using (StreamWriter sw = new StreamWriter(outputfile))
                {
                    foreach (string line in labstring)
                    {
                        sw.WriteLine(line);
                    }
                }
            //}
            //catch (Exception e)
            //{
            //    Console.WriteLine(e.Message);
            //}

        }

        private static void modifyphonename(string phonefile,string statefile, string outputfile)
        {
            string[] standardPhoneArray = File.ReadAllLines(phonefile);
            List<string> alignedPhoneList = new List<string>();
            for(int i=0;i< standardPhoneArray.Length;i++)
            {
                alignedPhoneList.Add(standardPhoneArray[i]);
            }
            string[] stateOriginalArray = File.ReadAllLines(statefile);
            if(stateOriginalArray.Length/5!= standardPhoneArray.Length)
            {
                Console.WriteLine("The number is not match between state and phone file");
            }
            Regex pattern = new Regex(@"-[a-zA-Z_]+\+");
            for (int i = 0; i < alignedPhoneList.Count; i++)
            {
                string[] tmp = alignedPhoneList[i].Split(' ', '\t');
                string match = pattern.Match(stateOriginalArray[i * 5]).Value;
                string key = Regex.Replace(match, "[-+]", "");
                //key = key.ToLower();
                string retemp = tmp[1] == "sil" ? "SIL":tmp[1];
                if (tmp[1] != key.ToLower())
                {
                    string replace = "-" + retemp + "+";
                    stateOriginalArray[i * 5] = Regex.Replace(stateOriginalArray[i * 5], match, replace);
                    stateOriginalArray[i * 5 + 1] = Regex.Replace(stateOriginalArray[i * 5 + 1], match, replace);
                    stateOriginalArray[i * 5 + 2] = Regex.Replace(stateOriginalArray[i * 5 + 2], match, replace);
                    stateOriginalArray[i * 5 + 3] = Regex.Replace(stateOriginalArray[i * 5 + 3], match, replace);
                    stateOriginalArray[i * 5 + 4] = Regex.Replace(stateOriginalArray[i * 5 + 4], match, replace);
                }
                if (i != 0)
                  {
                    string replace = @"+" + retemp + @"+";
                    //get last 5lines +phone+
                    string keylast = Regex.Match(stateOriginalArray[(i - 1) * 5], @"(?<=\+)\w+(?=\+)", RegexOptions.IgnoreCase).Value;                     
                    if(tmp[1]!= keylast.ToLower())
                    {
                        string fwKey = @"\+" + keylast + @"\+";
                        stateOriginalArray[(i - 1) * 5] = Regex.Replace(stateOriginalArray[(i - 1) * 5], fwKey, replace);
                        stateOriginalArray[(i - 1) * 5 + 1] = Regex.Replace(stateOriginalArray[(i - 1) * 5 + 1], fwKey, replace);
                        stateOriginalArray[(i - 1) * 5 + 2] = Regex.Replace(stateOriginalArray[(i - 1) * 5 + 2], fwKey, replace);
                        stateOriginalArray[(i - 1) * 5 + 3] = Regex.Replace(stateOriginalArray[(i - 1) * 5 + 3], fwKey, replace);
                        stateOriginalArray[(i - 1) * 5 + 4] = Regex.Replace(stateOriginalArray[(i - 1) * 5 + 4], fwKey, replace);
                    }

                    if (i < alignedPhoneList.Count - 1)
                    {
                        string replacenext = retemp + "-";
                        string keynext = Regex.Match(stateOriginalArray[(i+1) * 5], @"(?<=\s+)\w+(?=\-)", RegexOptions.IgnoreCase).Value;
                        if (tmp[1] != keynext.ToLower())
                        {
                            string bwKey = keynext + "-";
                            stateOriginalArray[(i + 1) * 5] = Regex.Replace(stateOriginalArray[(i + 1) * 5], bwKey, replacenext);
                            stateOriginalArray[(i + 1) * 5 + 1] = Regex.Replace(stateOriginalArray[(i + 1) * 5 + 1], bwKey, replacenext);
                            stateOriginalArray[(i + 1) * 5 + 2] = Regex.Replace(stateOriginalArray[(i + 1) * 5 + 2], bwKey, replacenext);
                            stateOriginalArray[(i + 1) * 5 + 3] = Regex.Replace(stateOriginalArray[(i + 1) * 5 + 3], bwKey, replacenext);
                            stateOriginalArray[(i + 1) * 5 + 4] = Regex.Replace(stateOriginalArray[(i + 1) * 5 + 4], bwKey, replacenext);
                        }

                    }
                    if (i < alignedPhoneList.Count - 2)
                    {
                        string replace2next = "+" + retemp + "|";
                        string keyn2ext = Regex.Match(stateOriginalArray[(i+2) * 5], @"(?<=\+)\w+(?=\|)", RegexOptions.IgnoreCase).Value;                   
                        if (tmp[1] != keyn2ext.ToLower())
                        {
                            string bwKey = @"\+" + keyn2ext + @"\|";
                            stateOriginalArray[(i + 2) * 5] = Regex.Replace(stateOriginalArray[(i + 2) * 5], bwKey, replace2next);
                            stateOriginalArray[(i + 2) * 5 + 1] = Regex.Replace(stateOriginalArray[(i + 2) * 5 + 1], bwKey, replace2next);
                            stateOriginalArray[(i + 2) * 5 + 2] = Regex.Replace(stateOriginalArray[(i + 2) * 5 + 2], bwKey, replace2next);
                            stateOriginalArray[(i + 2) * 5 + 3] = Regex.Replace(stateOriginalArray[(i + 2) * 5 + 3], bwKey, replace2next);
                            stateOriginalArray[(i + 2) * 5 + 4] = Regex.Replace(stateOriginalArray[(i + 2) * 5 + 4], bwKey, replace2next);
                        }

                    }
                    if(i>1)
                    {
                        string replace2next = "|" + retemp + "&";
                        string keyn2last = Regex.Match(stateOriginalArray[(i - 2) * 5], @"(?<=\|)\w+(?=\&)", RegexOptions.IgnoreCase).Value;
                        if (tmp[1] != keyn2last.ToLower())
                        {
                            string laKey = @"\|" + keyn2last + @"\&";
                            stateOriginalArray[(i - 2) * 5] = Regex.Replace(stateOriginalArray[(i - 2) * 5], laKey, replace2next);
                            stateOriginalArray[(i - 2) * 5 + 1] = Regex.Replace(stateOriginalArray[(i - 2) * 5 + 1], laKey, replace2next);
                            stateOriginalArray[(i - 2) * 5 + 2] = Regex.Replace(stateOriginalArray[(i - 2) * 5 + 2], laKey, replace2next);
                            stateOriginalArray[(i - 2) * 5 + 3] = Regex.Replace(stateOriginalArray[(i - 2) * 5 + 3], laKey, replace2next);
                            stateOriginalArray[(i - 2) * 5 + 4] = Regex.Replace(stateOriginalArray[(i - 2) * 5 + 4], laKey, replace2next);
                        }
                    }

                }
                
                }

            string path = Path.GetDirectoryName(statefile);
            using (StreamWriter sw = new StreamWriter(outputfile))
            {
                for (int i = 0; i < stateOriginalArray.Length; i++)
                {
                    sw.WriteLine(stateOriginalArray[i]);
                }
            }
            
        }



    }
}
