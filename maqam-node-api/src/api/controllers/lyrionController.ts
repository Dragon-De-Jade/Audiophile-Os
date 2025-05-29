import { Request, Response } from 'express';
import { getLyrionStatus, sendLyrionCommand } from '../../services/lyrionApiService';

export const getLyrionStatusController = async (req: Request, res: Response): Promise<void> => {
  try {
    const status = await getLyrionStatus();
    res.status(200).json({
      status: 'success',
      data: status,
    });
  } catch (error) {
    console.error('Error in getLyrionStatusController:', error);
    res.status(500).json({
      status: 'error',
      message: 'Failed to get Lyrion status.',
    });
  }
};

export const sendLyrionCommandController = async (req: Request, res: Response): Promise<void> => {
  try {
    const { command, params } = req.body;

    if (!command || typeof command !== 'string') {
      res.status(400).json({
        status: 'error',
        message: 'Invalid command provided. "command" must be a non-empty string.',
      });
      return;
    }

    const result = await sendLyrionCommand(command, params);
    res.status(200).json({
      status: 'success',
      data: result,
    });
  } catch (error) {
    console.error('Error in sendLyrionCommandController:', error);
    res.status(500).json({
      status: 'error',
      message: 'Failed to send command to Lyrion.',
    });
  }
};
