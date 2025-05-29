import { Request, Response } from 'express';
import { getSqueezeliteStatus, sendSqueezeliteCommand } from '../../services/squeezeliteApiService';

export const getSqueezeliteStatusController = async (req: Request, res: Response): Promise<void> => {
  try {
    const status = await getSqueezeliteStatus();
    res.status(200).json({
      status: 'success',
      data: status,
    });
  } catch (error) {
    console.error('Error in getSqueezeliteStatusController:', error);
    res.status(500).json({
      status: 'error',
      message: 'Failed to get Squeezelite status.',
    });
  }
};

export const sendSqueezeliteCommandController = async (req: Request, res: Response): Promise<void> => {
  try {
    const { command, params } = req.body;

    if (!command || typeof command !== 'string') {
      res.status(400).json({
        status: 'error',
        message: 'Invalid command provided. "command" must be a non-empty string.',
      });
      return;
    }

    const result = await sendSqueezeliteCommand(command, params);
    res.status(200).json({
      status: 'success',
      data: result,
    });
  } catch (error) {
    console.error('Error in sendSqueezeliteCommandController:', error);
    res.status(500).json({
      status: 'error',
      message: 'Failed to send command to Squeezelite.',
    });
  }
};
