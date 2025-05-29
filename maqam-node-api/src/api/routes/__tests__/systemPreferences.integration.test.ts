import request from 'supertest';
import app from '../../../app'; // Adjust path to your app's entry point
import { UserPreferences, DEFAULT_PREFERENCES } from '../../../services/userPreferencesService';

// Mock the userPreferencesService
const mockLoadPreferences = jest.fn();
const mockSavePreferences = jest.fn();

jest.mock('../../../services/userPreferencesService', () => ({
  loadPreferences: () => mockLoadPreferences(),
  savePreferences: (prefs: UserPreferences) => mockSavePreferences(prefs),
  // Exporting DEFAULT_PREFERENCES from the mock as well if it's used by the controller directly
  // or ensure the controller gets it from the mocked loadPreferences.
  // For this setup, the controller uses loadPreferences to get defaults if file not found.
  DEFAULT_PREFERENCES: { language: 'fr', theme: 'dark' }, 
}));


describe('Preferences API Endpoints (/api/system/preferences)', () => {
  const validApiKey = 'test-api-key';
  const invalidApiKey = 'invalid-api-key';
  let originalEnv: NodeJS.ProcessEnv;

  beforeAll(() => {
    originalEnv = { ...process.env };
    process.env.NODE_API_KEY = validApiKey; // Set a test API key
  });

  afterAll(() => {
    process.env = originalEnv; // Restore original environment
  });

  beforeEach(() => {
    // Reset mocks before each test
    mockLoadPreferences.mockReset();
    mockSavePreferences.mockReset();
    
    // Default mock implementations
    mockLoadPreferences.mockResolvedValue({ ...DEFAULT_PREFERENCES }); 
    mockSavePreferences.mockImplementation((prefs) => Promise.resolve(true)); 
  });

  describe('GET /api/system/preferences', () => {
    it('should return 401 if no API key is provided', async () => {
      const response = await request(app).get('/api/system/preferences');
      expect(response.status).toBe(401);
      expect(response.body.message).toContain('API Key missing or invalid');
    });

    it('should return 401 if an invalid API key is provided', async () => {
      const response = await request(app)
        .get('/api/system/preferences')
        .set('X-API-Key', invalidApiKey);
      expect(response.status).toBe(401);
      expect(response.body.message).toContain('API Key missing or invalid');
    });

    it('should return default preferences with a valid API key', async () => {
      // Mock loadPreferences to return specific default-like data
      const expectedPreferences = { language: 'fr', theme: 'dark' };
      mockLoadPreferences.mockResolvedValue(expectedPreferences);

      const response = await request(app)
        .get('/api/system/preferences')
        .set('X-API-Key', validApiKey);

      expect(response.status).toBe(200);
      expect(response.body.status).toBe('success');
      expect(response.body.data).toEqual(expectedPreferences);
      expect(mockLoadPreferences).toHaveBeenCalledTimes(1);
    });
    
    it('should return specific preferences if they are set', async () => {
      const specificPreferences = { language: 'en', theme: 'light' };
      mockLoadPreferences.mockResolvedValue(specificPreferences);

      const response = await request(app)
        .get('/api/system/preferences')
        .set('X-API-Key', validApiKey);

      expect(response.status).toBe(200);
      expect(response.body.data).toEqual(specificPreferences);
    });
  });

  describe('POST /api/system/preferences', () => {
    it('should return 401 if no API key is provided', async () => {
      const response = await request(app)
        .post('/api/system/preferences')
        .send({ theme: 'light' });
      expect(response.status).toBe(401);
    });

    it('should return 401 if an invalid API key is provided', async () => {
      const response = await request(app)
        .post('/api/system/preferences')
        .set('X-API-Key', invalidApiKey)
        .send({ theme: 'light' });
      expect(response.status).toBe(401);
    });

    it('should update preferences and return them with a valid API key', async () => {
      const newPrefs: Partial<UserPreferences> = { theme: 'light', language: 'en' };
      const expectedSavedPrefs = { ...DEFAULT_PREFERENCES, ...newPrefs };
      
      // savePreferences mock will be called with newPrefs
      // loadPreferences will be called after save to return the "updated" state
      mockSavePreferences.mockResolvedValue(true);
      mockLoadPreferences.mockResolvedValue(expectedSavedPrefs); // Simulate that save was successful and new prefs are loaded

      const response = await request(app)
        .post('/api/system/preferences')
        .set('X-API-Key', validApiKey)
        .send(newPrefs);

      expect(response.status).toBe(200);
      expect(response.body.status).toBe('success');
      expect(response.body.message).toBe('Preferences updated successfully.');
      expect(response.body.data).toEqual(expectedSavedPrefs);
      expect(mockSavePreferences).toHaveBeenCalledWith(newPrefs);
      expect(mockLoadPreferences).toHaveBeenCalledTimes(1); // Called by the controller to return the updated prefs
    });

    it('should only save known preference keys and return merged preferences', async () => {
      const newPrefs = { theme: 'solarized', unknownKey: 'shouldBeIgnored', language: 'de' };
      // The service itself handles filtering, but the controller receives the raw body.
      // The mockSavePreferences should ideally reflect the filtering logic if we were testing it directly.
      // However, here we're testing the controller, which passes the body to the service.
      // The service is mocked, so we ensure it's called with the correct data.
      // The controller then calls loadPreferences to get the "current" state.
      
      const expectedSavedPrefs = { language: 'de', theme: 'solarized' }; // Assuming unknownKey is filtered by service
      mockSavePreferences.mockResolvedValue(true); // Assume save is successful
      // Simulate that the service correctly saved and filtered, and now load returns the correct state
      mockLoadPreferences.mockResolvedValue({ ...DEFAULT_PREFERENCES, ...expectedSavedPrefs });


      const response = await request(app)
        .post('/api/system/preferences')
        .set('X-API-Key', validApiKey)
        .send(newPrefs);

      expect(response.status).toBe(200);
      expect(mockSavePreferences).toHaveBeenCalledWith(newPrefs); // Controller passes everything to service
      // The response data should reflect what loadPreferences (mocked) returns after a successful save
      expect(response.body.data).toEqual({ ...DEFAULT_PREFERENCES, ...expectedSavedPrefs });
    });

    it('should return 400 if an empty object is sent', async () => {
      const response = await request(app)
        .post('/api/system/preferences')
        .set('X-API-Key', validApiKey)
        .send({});
      
      expect(response.status).toBe(400);
      expect(response.body.message).toContain('Invalid preferences data provided');
    });
    
    it('should return 400 if non-object data is sent', async () => {
      const response = await request(app)
        .post('/api/system/preferences')
        .set('X-API-Key', validApiKey)
        .send("not-an-object");
      
      expect(response.status).toBe(400);
      expect(response.body.message).toContain('Invalid preferences data provided');
    });

     it('should return 500 if savePreferences fails', async () => {
      mockSavePreferences.mockResolvedValue(false); // Simulate failure in saving

      const response = await request(app)
        .post('/api/system/preferences')
        .set('X-API-Key', validApiKey)
        .send({ theme: 'night' });

      expect(response.status).toBe(500);
      expect(response.body.message).toBe('Failed to save preferences.');
    });

  });
});
