import fs from "fs";
import path from "path";
import { Extract } from "unzipper";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const pbixPath = path.join(__dirname, "lab.pbix");
const tempPath = path.join(__dirname, ".pbix_list_temp");

// Clean up if exists
if (fs.existsSync(tempPath)) {
  fs.rmSync(tempPath, { recursive: true });
}

fs.createReadStream(pbixPath)
  .pipe(Extract({ path: tempPath }))
  .on("close", () => {
    console.log("PBIX Full Structure:");
    const listDir = (dir, prefix = "", maxDepth = 5, currentDepth = 0) => {
      if (currentDepth >= maxDepth) return;
      const files = fs.readdirSync(dir);
      files.forEach((file) => {
        const fullPath = path.join(dir, file);
        const stat = fs.statSync(fullPath);
        if (stat.isDirectory()) {
          console.log(`${prefix}📁 ${file}/`);
          listDir(fullPath, prefix + "  ", maxDepth, currentDepth + 1);
        } else {
          const size = stat.size;
          console.log(`${prefix}📄 ${file} (${size} bytes)`);
          // Show content of small JSON files
          if (file.endsWith(".json") && size < 50000) {
            try {
              const content = fs.readFileSync(fullPath, "utf8");
              const contentPreview = content.substring(0, 200);
              console.log(`${prefix}   └─ ${contentPreview}...`);
            } catch (e) {}
          }
        }
      });
    };
    listDir(tempPath);
    
    // Clean up
    fs.rmSync(tempPath, { recursive: true });
  })
  .on("error", (err) => {
    console.error("Error:", err.message);
  });
