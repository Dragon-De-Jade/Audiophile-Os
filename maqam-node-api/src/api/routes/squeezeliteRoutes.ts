import { Router } from 'express';
import { getSqueezeliteStatusController, sendSqueezeliteCommandController } from '../controllers/squeezeliteController';
import { apiKeyAuth } from '../middleware/authMiddleware';

const router = Router();

router.get('/status', apiKeyAuth, getSqueezeliteStatusController);
router.post('/command', apiKeyAuth, sendSqueezeliteCommandController);

export default router;
