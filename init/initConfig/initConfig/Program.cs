using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

namespace initConfig
{
    class Program
    {
        static void Main(string[] args)
        {
            //string curDirectory = Environment.CurrentDirectory;
            string curDirectory = @"E:\shihliu\code\MerlinIntegration_git\1st_Version\tool";
            string templateDir = Path.Combine(curDirectory, "input/ConfigTemplate");
            string outputDir = Path.Combine(curDirectory, "input");

            DirectoryInfo templateFolder = new DirectoryInfo(templateDir);
            FileInfo[] templateFiles = templateFolder.GetFiles();
            string replacement = @"${currentFolder}";

            foreach (FileInfo fi in templateFiles)
            {
                string[] tmp = fi.Name.Split('.');
                string fileId = tmp[0];
                string outputFilePath = Path.Combine(outputDir, fileId + fi.Extension);
                string reCurDirectory = (fileId == "linguisticExtraction" || fileId == "WavGeneration" || fileId == "WavGeneration_f0label") ?
                                        curDirectory.Replace("\\", "/") : curDirectory;
                string[] lines = File.ReadAllLines(fi.FullName);
                for(int i = 0; i < lines.Length; i++)
                {
                    if (lines[i].Contains(replacement))
                    {
                        lines[i] = lines[i].Replace(replacement, reCurDirectory);
                    }
                }

                using(StreamWriter sw = new StreamWriter(outputFilePath))
                {
                    for(int i = 0; i < lines.Length; i++)
                    {
                        sw.WriteLine(lines[i]);
                    }
                }
            }
        }
    }
}
