import AdmZip from "adm-zip";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const pbixPath = path.join(__dirname, "lab.pbix");
const zip = new AdmZip(pbixPath);
const entries = zip.getEntries();

console.log("PBIX Contents:");
entries.slice(0, 30).forEach((entry) => {
  console.log(`  ${entry.entryName} (${entry.isDirectory ? "dir" : "file"})`);
});

if (entries.length > 30) {
  console.log(`  ... and ${entries.length - 30} more entries`);
}
