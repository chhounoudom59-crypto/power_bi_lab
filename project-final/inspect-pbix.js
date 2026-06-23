import fs from "fs";
import path from "path";
import { Extract } from "unzipper";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const pbixPath = path.join(__dirname, "lab.pbix");
const tempPath = path.join(__dirname, ".pbix_inspect_temp");

// Clean up if exists
if (fs.existsSync(tempPath)) {
  fs.rmSync(tempPath, { recursive: true });
}

fs.createReadStream(pbixPath)
  .pipe(Extract({ path: tempPath }))
  .on("close", () => {
    console.log("=== Metadata ===");
    try {
      const metadata = fs.readFileSync(path.join(tempPath, "Metadata"), "utf8");
      console.log(metadata);
    } catch (e) {
      console.log("Could not read as text");
    }

    console.log("\n=== DataModel (first 500 chars) ===");
    try {
      const dataModel = fs.readFileSync(path.join(tempPath, "DataModel"), "utf8");
      console.log(dataModel.substring(0, 500));
    } catch (e) {
      console.log("Binary file, trying as buffer");
      const dataModel = fs.readFileSync(path.join(tempPath, "DataModel"));
      console.log("Buffer length:", dataModel.length);
      console.log("First 200 bytes as string:", dataModel.toString("utf8", 0, 200));
    }

    // Clean up
    fs.rmSync(tempPath, { recursive: true });
  })
  .on("error", (err) => {
    console.error("Error:", err.message);
  });
