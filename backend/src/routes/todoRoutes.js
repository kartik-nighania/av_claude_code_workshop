// Route table for the /api/todos resource.

import { Router } from "express";
import * as controller from "../controllers/todoController.js";

const router = Router();

router.get("/", controller.list);
router.post("/", controller.create);
router.get("/:id", controller.getOne);
router.put("/:id", controller.update);
router.patch("/:id/toggle", controller.toggle);
router.delete("/:id", controller.remove);

export default router;
