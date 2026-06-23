import { spawn } from "child_process";

const serverProcess = spawn("node", ["server.js"], {
  stdio: "inherit",
  cwd: process.cwd(),
});

serverProcess.on("error", (err) => {
  console.error("Failed to start server:", err);
});

serverProcess.on("exit", (code) => {
  console.log("Server exited with code:", code);
});

// Keep the process running
setTimeout(() => {
  serverProcess.kill();
}, 5000);
