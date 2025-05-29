import { promises as fs } from 'fs';
import path from 'path';

export interface UserPreferences {
  language: string;
  theme: string;
  // Add other preferences here as needed
}

export const DEFAULT_PREFERENCES: UserPreferences = {
  language: 'fr',
  theme: 'dark',
};

// Resolves to maqam-node-api/user_preferences.json when running from dist/services/userPreferencesService.js
// Or maqam-node-api/user_preferences.json when running with ts-node from src/services/userPreferencesService.ts (if __dirname refers to src)
// For ts-node, __dirname is the directory of the current .ts file.
// For compiled JS, __dirname is the directory of the compiled .js file (e.g., dist/services).
const PREFERENCES_FILE_PATH = path.join(__dirname, '..', '..', 'user_preferences.json');


export const loadPreferences = async (): Promise<UserPreferences> => {
  try {
    await fs.access(PREFERENCES_FILE_PATH);
    const data = await fs.readFile(PREFERENCES_FILE_PATH, 'utf-8');
    const loadedPrefs = JSON.parse(data) as Partial<UserPreferences>;
    
    // Merge with defaults to ensure all keys are present and handle partial saves
    const mergedPreferences = { ...DEFAULT_PREFERENCES, ...loadedPrefs };
    console.info('Preferences loaded successfully.');
    return mergedPreferences;
  } catch (error) {
    if (error instanceof Error && 'code' in error && error.code === 'ENOENT') {
      console.info('Preferences file not found. Returning default preferences.');
    } else {
      console.error('Error loading preferences:', error);
    }
    return { ...DEFAULT_PREFERENCES }; // Return a copy
  }
};

export const savePreferences = async (prefs: UserPreferences): Promise<boolean> => {
  try {
    // Basic validation: Ensure only known keys from UserPreferences are saved
    const validKeys = Object.keys(DEFAULT_PREFERENCES) as (keyof UserPreferences)[];
    const validatedPrefs: Partial<UserPreferences> = {};
    let hasValidKeys = false;

    for (const key of validKeys) {
      if (key in prefs && typeof prefs[key] === typeof DEFAULT_PREFERENCES[key]) {
        validatedPrefs[key] = prefs[key];
        hasValidKeys = true;
      } else if (key in prefs) {
        // Log a warning if a key exists but type is wrong, and don't save it.
        console.warn(`Invalid type for preference key: ${key}. Using default value.`);
        validatedPrefs[key] = DEFAULT_PREFERENCES[key]; // Fallback to default for this key
      }
    }

    if (!hasValidKeys && Object.keys(prefs).length > 0) {
        console.warn('No valid preference keys provided or all keys had type mismatches. Saving default preferences instead.');
        await fs.writeFile(PREFERENCES_FILE_PATH, JSON.stringify(DEFAULT_PREFERENCES, null, 2));
        return true; // Saved defaults
    } else if (!hasValidKeys && Object.keys(prefs).length === 0) {
        console.info('No preferences provided to save. Current file remains unchanged or default will be used on next load if no file exists.');
        // Decide if an empty object should clear the file or be a no-op
        // For now, let's not write an empty object, effectively a no-op if no valid keys.
        // Or, if we want to ensure a file with defaults is created even with empty input:
        // await fs.writeFile(PREFERENCES_FILE_PATH, JSON.stringify(DEFAULT_PREFERENCES, null, 2));
        // return true; 
        return false; // Or indicate no actual save happened for an empty valid object
    }


    await fs.writeFile(PREFERENCES_FILE_PATH, JSON.stringify(hasValidKeys ? validatedPrefs : DEFAULT_PREFERENCES, null, 2));
    console.info('Preferences saved successfully.');
    return true;
  } catch (error) {
    console.error('Error saving preferences:', error);
    return false;
  }
};
