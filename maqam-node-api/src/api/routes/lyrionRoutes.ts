import { Router } from 'express';
import { getLyrionStatusController, sendLyrionCommandController } from '../controllers/lyrionController';
import { apiKeyAuth } from '../middleware/authMiddleware';

const router = Router();

router.get('/status', apiKeyAuth, getLyrionStatusController);
router.post('/command', apiKeyAuth, sendLyrionCommandController);

export default router;
