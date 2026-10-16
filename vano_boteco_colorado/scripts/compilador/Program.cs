using System;
using System.IO;
using System.Xml;
using CodeWalker.GameFiles;
class Program {
static int Main(string[] args) {
 string root=Path.GetFullPath(args[0]),tools=args.Length>1?args[1]:"/workspace/tools";
 string strings=Path.Combine(AppContext.BaseDirectory,"strings.txt");
 if(!File.Exists(strings))strings=Path.Combine(tools,"CodeWalker/CodeWalker.Core/strings.txt");
 if(File.Exists(strings))foreach(var line in File.ReadAllLines(strings))if(!line.StartsWith("//"))JenkIndex.Ensure(line.Trim());
 foreach(var p in Directory.GetFiles(Path.Combine(root,"xml"),"*.xml")) {
 var source=new XmlDocument();source.Load(p);
 foreach(XmlNode leaf in source.SelectNodes("//*[not(*)]")) {
 string name=leaf.InnerText.Trim();if(name.Length>0 && name.Length<=256 && !name.Contains("\n"))JenkIndex.Ensure(name);
 }
 }
 foreach(var p in Directory.GetFiles(Path.Combine(root,"xml"),"*.xml"))JenkIndex.Ensure(Path.GetFileName(p).Replace(".xml","").Split('.')[0]);
 Directory.CreateDirectory(Path.Combine(root,"relatorios/roundtrip"));int fail=0,ok=0;
 foreach(var p in Directory.GetFiles(Path.Combine(root,"xml"),"*.xml")) {
 string name=Path.GetFileNameWithoutExtension(p),ext=Path.GetExtension(name),stem=Path.GetFileNameWithoutExtension(name);XmlDocument doc=new XmlDocument();doc.Load(p);
 try {
 MetaFormat fmt=ext==".ydr"?MetaFormat.Ydr:ext==".ybn"?MetaFormat.Ybn:ext==".ytd"?MetaFormat.Ytd:MetaFormat.RSC;
 byte[] data=XmlMeta.GetData(doc,fmt,Path.Combine(root,"xml",stem));if(data==null||data.Length<=16)throw new Exception("No binary data generated");
 string folder=ext==".ymap"?"exemplos":"stream";File.WriteAllBytes(Path.Combine(root,folder,name),data);
 string xml=null,fn;
 switch(ext) {
 case ".ydr":var dr=new YdrFile();dr.Load(data);dr.Name=name;if(dr.Drawable==null)throw new Exception("Roundtrip Drawable null");xml=MetaXml.GetXml(dr,out fn,"");break;
 case ".ybn":var bn=new YbnFile();bn.Load(data);bn.Name=name;if(bn.Bounds==null)throw new Exception("Roundtrip Bounds null");xml=MetaXml.GetXml(bn,out fn);break;
 case ".ytd":var td=new YtdFile();td.Load(data);td.Name=name;if(td.TextureDict==null)throw new Exception("Roundtrip TextureDict null");xml=MetaXml.GetXml(td,out fn,"");break;
 case ".ytyp":var typ=new YtypFile();typ.Load(data);typ.Name=name;xml=MetaXml.GetXml(typ,out fn);break;
 case ".ymap":var map=new YmapFile();map.Load(data);map.Name=name;xml=MetaXml.GetXml(map,out fn);break;
 }
 XmlDocument verify=new XmlDocument();verify.LoadXml(xml);File.WriteAllText(Path.Combine(root,"relatorios/roundtrip",name+".xml"),xml);Console.WriteLine($"OK {name}: {data.Length} bytes, reloaded and XML parsed");ok++;
 }catch(Exception e){Console.WriteLine("FAIL "+name+" "+e);fail++;}
 }
 Console.WriteLine($"Compiled {ok}; failed {fail}");return fail>0?1:0;
}}
