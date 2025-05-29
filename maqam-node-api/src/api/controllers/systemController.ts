import { Request, Response } from 'express';
import { loadPreferences, savePreferences, UserPreferences } from '../../services/userPreferencesService';
import { version as apiVersion } from '../../../package.json';


export const getSystemInfoController = (req: Request, res: Response): void => {
  try {
    const systemInfo = {
      apiVersion,
      nodeVersion: process.version,
      platform: process.platform,
      status: "running",
    };
    res.status(200).json({
      status: 'success',
      data: systemInfo,
    });
  } catch (error) {
    console.error('Error in getSystemInfoController:', error);
    res.status(500).json({
      status: 'error',
      message: 'Failed to get system information.',
    });
  }
};

export const getPreferencesController = async (req: Request, res: Response): Promise<void> => {
  try {
    const preferences = await loadPreferences();
    res.status(200).json({
      status: 'success',
      data: preferences,
    });
  } catch (error) {
    console.error('Error in getPreferencesController:', error);
    res.status(500).json({
      status: 'error',
      message: 'Failed to load preferences.',
    });
  }
};

export const updatePreferencesController = async (req: Request, res: Response): Promise<void> => {
  try {
    const newPreferences = req.body as Partial<UserPreferences>; // Cast to partial to allow for partial updates

    // Validate that newPreferences is an object and not empty
    if (typeof newPreferences !== 'object' || newPreferences === null || Object.keys(newPreferences).length === 0) {
      res.status(400).json({
        status: 'error',
        message: 'Invalid preferences data provided. Request body must be a non-empty JSON object.',
      });
      return;
    }
    
    // The savePreferences service function already handles merging with defaults and validating keys.
    const success = await savePreferences(newPreferences as UserPreferences); // Cast to UserPreferences for the service

    if (success) {
      const updatedPreferences = await loadPreferences(); // Load the merged and saved preferences
      res.status(200).json({
        status: 'success',
        message: 'Preferences updated successfully.',
        data: updatedPreferences,
      });
    } else {
      // savePreferences logs specific errors, so a generic message here is okay.
      res.status(500).json({
        status: 'error',
        message: 'Failed to save preferences.',
      });
    }
  } catch (error) {
    console.error('Error in updatePreferencesController:', error);
    res.status(500).json({
      status: 'error',
      message: 'An unexpected error occurred while updating preferences.',
    });
  }
};
