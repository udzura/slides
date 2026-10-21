import AppKit
import CoreImage
import Foundation

let url = "https://udzura.jp/slides/2026/fukuokawasm-1/"
let directory = URL(fileURLWithPath: #filePath).deletingLastPathComponent()
let output = directory.appendingPathComponent("images/slides-qr.png")
let context = CIContext()
let filter = CIFilter(name: "CIQRCodeGenerator")!
filter.setValue(Data(url.utf8), forKey: "inputMessage")
filter.setValue("M", forKey: "inputCorrectionLevel")

// Preserve square modules and a four-module white quiet zone on every side.
let scale: CGFloat = 16
let qr = filter.outputImage!.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
let bounds = qr.extent.insetBy(dx: -4 * scale, dy: -4 * scale)
let background = CIImage(color: .white).cropped(to: bounds)
guard let image = context.createCGImage(qr.composited(over: background), from: bounds) else {
    throw NSError(domain: "SlideQRCode", code: 1,
                  userInfo: [NSLocalizedDescriptionKey: "Core Image could not render the QR code"])
}
let bitmap = NSBitmapImageRep(cgImage: image)
try bitmap.representation(using: .png, properties: [:])!.write(to: output)

// Decode the saved image to verify the exact URL, including its trailing slash.
let detector = CIDetector(ofType: CIDetectorTypeQRCode, context: context,
                          options: [CIDetectorAccuracy: CIDetectorAccuracyHigh])!
let saved = CIImage(contentsOf: output)!
let codes = detector.features(in: saved).compactMap { ($0 as? CIQRCodeFeature)?.messageString }
precondition(codes == [url], "QR code did not decode to the expected slide URL")
print("Saved \(output.path) (\(image.width) × \(image.height)); verified: \(url)")
