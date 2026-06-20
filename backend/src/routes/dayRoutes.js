// Route table for the /api/days resource.

import { Router } from "express";
import * as controller from "../controllers/dayController.js";

const router = Router();

router.get("/", controller.list);
router.get("/:date", controller.getOne);
router.patch("/:date", controller.update);

export default router;
