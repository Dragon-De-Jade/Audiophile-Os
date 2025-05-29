import { Router } from 'express';
import { getPreferencesController, updatePreferencesController, getSystemInfoController } from '../controllers/systemController';
import { apiKeyAuth } from '../middleware/authMiddleware';

const router = Router();

router.get('/info', getSystemInfoController); // Not protected by API key
router.get('/preferences', apiKeyAuth, getPreferencesController);
router.post('/preferences', apiKeyAuth, updatePreferencesController);

export default router;
