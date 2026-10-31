import Foundation
import Vision
import AppKit
let dir = CommandLine.arguments[1]
let fm = FileManager.default
var out:[String:Any]=[:]
for f in try! fm.contentsOfDirectory(atPath: dir).sorted() where f.hasSuffix(".jpg") {
  let url = URL(fileURLWithPath: dir+"/"+f)
  let req = VNRecognizeTextRequest()
  req.recognitionLevel = .accurate
  req.recognitionLanguages = ["zh-Hans","en-US"]
  req.usesLanguageCorrection = false
  let h = VNImageRequestHandler(url:url,options:[:])
  try! h.perform([req])
  var items:[[String:Any]]=[]
  for o in req.results ?? [] {
    guard let c = o.topCandidates(1).first else {continue}
    var chars:[[Any]]=[]
    let s=c.string
    var i=s.startIndex
    while i<s.endIndex { let n=s.index(after:i)
      if let b = try? c.boundingBox(for:i..<n) { let r=b.boundingBox; chars.append([String(s[i..<n]),r.minX,r.minY,r.width,r.height]) }
      i=n }
    items.append(["text":s,"conf":c.confidence,"chars":chars])
  }
  out[f]=items
}
let d = try! JSONSerialization.data(withJSONObject: out, options:[])
FileManager.default.createFile(atPath: CommandLine.arguments[2], contents:d)
