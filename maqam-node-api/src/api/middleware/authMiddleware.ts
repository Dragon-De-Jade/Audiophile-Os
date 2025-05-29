import { Request, Response, NextFunction } from 'express';

export const apiKeyAuth = (req: Request, res: Response, next: NextFunction) => {
  const apiKey = req.header('X-API-Key');
  const expectedApiKey = process.env.NODE_API_KEY || 'supersecretkey';

  if (process.env.NODE_API_KEY === undefined) {
    console.warn('Warning: NODE_API_KEY is not set. Using default API key for development.');
  }

  if (apiKey && apiKey === expectedApiKey) {
    next();
  } else {
    res.status(401).json({
      status: 'error',
      message: 'Unauthorized: API Key missing or invalid',
    });
  }
};
