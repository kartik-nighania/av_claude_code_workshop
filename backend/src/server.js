// Entry point: binds the Express app to a port.

import { createApp } from "./app.js";

const PORT = process.env.PORT || 3001;
const app = createApp();

app.listen(PORT, () => {
  console.log(`Health Tracker API listening on http://localhost:${PORT}`);
});
