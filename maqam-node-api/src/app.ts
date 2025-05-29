import express, { Application, Request, Response } from 'express';

const app: Application = express();

app.use(express.json()); // Middleware to parse JSON bodies

app.get('/', (req: Request, res: Response) => {
  res.send('MAQAM Node.js API is running!');
});

// Placeholder for future routes
import systemRoutes from './api/routes/systemRoutes';
app.use('/api/system', systemRoutes);

import lyrionRoutes from './api/routes/lyrionRoutes';
app.use('/api/lyrion', lyrionRoutes);

import squeezeliteRoutes from './api/routes/squeezeliteRoutes';
app.use('/api/squeezelite', squeezeliteRoutes);

// import { apiKeyAuth } from './api/middleware/authMiddleware';
// app.use('/api/protectedroute', apiKeyAuth, (req, res) => {
//   res.json({ message: 'This is a protected route' });
// });

export default app;
