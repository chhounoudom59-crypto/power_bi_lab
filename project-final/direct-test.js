import fs from "fs";
import path from "path";
import { Extract } from "unzipper";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function getPBIXPath() {
  const paths = [
    path.join(__dirname, "lab.pbix"),
    path.join(__dirname, "..", "lab.pbix"),
  ];
  console.log("🔍 Looking for PBIX at:");
  paths.forEach((p) => console.log(`  - ${p} (exists: ${fs.existsSync(p)})`));

  for (const p of paths) {
    if (fs.existsSync(p)) return p;
  }
  return path.join(__dirname, "lab.pbix");
}

async function extractPBIXModel(pbixPath) {
  if (!pbixPath) {
    throw new Error("PBIX path is undefined");
  }
  if (!fs.existsSync(pbixPath)) {
    throw new Error(`PBIX file not found at: ${pbixPath}`);
  }
  return new Promise((resolve, reject) => {
    const tempPath = path.join(__dirname, ".pbix_temp");
    fs.createReadStream(pbixPath)
      .pipe(Extract({ path: tempPath }))
      .on("close", () => {
        try {
          // Try to read Metadata file
          const metadataPath = path.join(tempPath, "Metadata");
          let metadata = null;
          
          if (fs.existsSync(metadataPath)) {
            try {
              const metadataContent = fs.readFileSync(metadataPath, "utf8");
              metadata = JSON.parse(metadataContent);
            } catch (e) {
              console.warn("Could not parse Metadata as JSON:", e.message);
              // Try reading as binary
              const buffer = fs.readFileSync(metadataPath);
              metadata = {
                raw: buffer.toString("hex").substring(0, 100),
                size: buffer.length
              };
            }
          }
          
          // Also try to read DataModel for additional info
          const dataModelPath = path.join(tempPath, "DataModel");
          let dataModelInfo = null;
          if (fs.existsSync(dataModelPath)) {
            const stats = fs.statSync(dataModelPath);
            dataModelInfo = {
              size: stats.size,
              compressed: true,
              format: "XPress9 (binary)"
            };
          }
          
          resolve({
            metadata,
            dataModel: dataModelInfo,
            pbixPath: path.basename(pbixPath)
          });
        } catch (err) {
          reject(err);
        }
      })
      .on("error", reject);
  });
}

function cleanupTemp() {
  const tempDir = path.join(__dirname, ".pbix_temp");
  if (fs.existsSync(tempDir)) {
    fs.rmSync(tempDir, { recursive: true });
  }
}

try {
  console.log("📂 Current directory:", __dirname);
  console.log("\n🔍 Locating PBIX file...");
  const pbixPath = getPBIXPath();
  console.log(`\n✅ Found PBIX at: ${pbixPath}`);

  console.log("\n📦 Extracting PBIX...");
  const pbixData = await extractPBIXModel(pbixPath);
  console.log("✅ Extraction successful!");

  const meta = pbixData.metadata || {};
  const dataModel = pbixData.dataModel || {};

  console.log(`\n📊 PBIX Summary:`);
  console.log(`   File: ${pbixData.pbixPath}`);
  console.log(`   Version: ${meta.Version || "unknown"}`);
  console.log(`   Created From: ${meta.CreatedFrom || "unknown"}`);
  console.log(`   Power BI Release: ${meta.CreatedFromRelease || "unknown"}`);
  console.log(`   Auto-created Relationships: ${meta.AutoCreatedRelationships?.length || 0}`);
  console.log(`   DataModel Compressed Format: ${dataModel.format || "unknown"}`);
  console.log(`   DataModel Size: ${dataModel.size ? (dataModel.size / 1024).toFixed(2) + " KB" : "unknown"}`);

  cleanupTemp();
  console.log("\n✅ Test passed!");
} catch (error) {
  console.error("❌ Error:", error.message);
  console.error(error.stack);
  process.exit(1);
}
