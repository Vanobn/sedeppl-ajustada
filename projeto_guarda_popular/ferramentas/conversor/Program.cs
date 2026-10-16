using System;
using System.IO;
using System.Collections.Generic;
using CodeWalker.GameFiles;
class Program {
static int Main(string[] args) {
 string toolRoot=args.Length>2?args[2]:"/workspace/tools";
 foreach(var line in File.ReadAllLines(Path.Combine(toolRoot,"CodeWalker/CodeWalker.Core/strings.txt")))if(!line.StartsWith("//"))JenkIndex.Ensure(line.Trim());
 foreach(var line in File.ReadAllLines(Path.Combine(toolRoot,"shader_names.txt")))JenkIndex.Ensure(line.Trim());
 foreach(var path in Directory.GetFiles(args[0]))JenkIndex.Ensure(Path.GetFileNameWithoutExtension(path).ToLower());
 Directory.CreateDirectory(args[1]);int fail=0,ok=0;
 foreach(var p in Directory.GetFiles(args[0],"*",SearchOption.TopDirectoryOnly)) {
 string ext=Path.GetExtension(p).ToLower(),name=Path.GetFileName(p),xml=null,fn;byte[] d;
 if(!new HashSet<string>{".ydr",".yft",".ytd",".ybn",".ytyp",".ymap"}.Contains(ext))continue;
 try {d=File.ReadAllBytes(p);
 switch(ext) {
 case ".ydr":var dr=new YdrFile();dr.Load(d);dr.Name=name;if(dr.Drawable==null)throw new Exception("Drawable null");xml=MetaXml.GetXml(dr,out fn,Path.Combine(args[1],"texturas_por_asset",name));break;
 case ".yft":var ft=new YftFile();ft.Load(d);ft.Name=name;if(ft.Fragment==null)throw new Exception("Fragment null");xml=MetaXml.GetXml(ft,out fn,Path.Combine(args[1],"texturas_por_asset",name));break;
 case ".ytd":var td=new YtdFile();td.Load(d);td.Name=name;if(td.TextureDict==null)throw new Exception("TextureDict null");xml=MetaXml.GetXml(td,out fn,Path.Combine(args[1],"texturas_por_asset",name));break;
 case ".ybn":var bn=new YbnFile();bn.Load(d);bn.Name=name;if(bn.Bounds==null)throw new Exception("Bounds null");xml=MetaXml.GetXml(bn,out fn);break;
 case ".ytyp":var typ=new YtypFile();typ.Load(d);typ.Name=name;xml=MetaXml.GetXml(typ,out fn);break;
 case ".ymap":var map=new YmapFile();map.Load(d);map.Name=name;xml=MetaXml.GetXml(map,out fn);break;
 }
 if(string.IsNullOrWhiteSpace(xml))throw new Exception("XML empty");File.WriteAllText(Path.Combine(args[1],name+".xml"),xml);Console.WriteLine("OK "+name);ok++;
 }catch(Exception e){Console.WriteLine("FAIL "+name+" "+e.ToString());fail++;}
 }
 Console.WriteLine($"Converted {ok}; failed {fail}");return fail>0?1:0;
}}
