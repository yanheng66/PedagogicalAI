const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const { writeToCollection, getAllDocs } = require("./firestoreAdmin");

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Sample route
app.get("/api/ping", (req, res) => {
  res.json({ message: "pong from backend!" });
});

// Firestore write
app.post("/api/admin/write", async (req, res) => {
  try {
    const id = await writeToCollection("students", req.body);
    res.json({ id });
  } catch (err) {
    res.status(500).json({ error: "Failed to write to Firestore" });
  }
});

// Firestore read
app.get("/api/admin/students", async (req, res) => {
  try {
    const students = await getAllDocs("students");
    res.json(students);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch students" });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
