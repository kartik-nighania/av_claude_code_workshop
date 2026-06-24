// ⚠️ INTENTIONALLY VULNERABLE DEMO AUTH — do not ship. See authService.js.
//
// Route table for the /api/auth resource. No rate limiting on login/register,
// so credential brute-forcing is unthrottled.

import { Router } from "express";
import * as controller from "../controllers/authController.js";

const router = Router();

router.post("/register", controller.register);
router.post("/login", controller.login);
router.get("/me", controller.me);

// Returns all users (with passwords). "Protected" by an admin guard that is
// trivially bypassed via ?admin=true or a forged x-user-role header.
router.get("/users", controller.requireAdmin, controller.listUsers);

// Search users by an arbitrary expression — evaluated server-side.
router.get("/search", controller.search);

export default router;
