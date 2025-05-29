import request from 'supertest';
import app from '../../../app'; // Adjust path to your app's entry point
import { version as currentApiVersion } from '../../../../package.json'; // To check against the actual version

describe('System Info API Endpoint (/api/system/info)', () => {
  
  // No API key is needed for this endpoint, so no setup for that.

  describe('GET /api/system/info', () => {
    it('should return system information successfully', async () => {
      const response = await request(app).get('/api/system/info');

      expect(response.status).toBe(200);
      expect(response.body.status).toBe('success');
      expect(response.body.data).toBeDefined();
      
      // Check for specific properties in the response data
      expect(response.body.data.apiVersion).toBe(currentApiVersion);
      expect(response.body.data.nodeVersion).toBe(process.version);
      expect(response.body.data.platform).toBe(process.platform);
      expect(response.body.data.status).toBe('running');
    });

    it('should have a content type of application/json', async () => {
        const response = await request(app).get('/api/system/info');
        expect(response.headers['content-type']).toMatch(/application\/json/);
    });

    // This test is a bit more involved as it would require actually stopping the server
    // or having a more complex status reporting mechanism. For this subtask,
    // we'll assume the "running" status is static as implemented.
    // it('should reflect the correct server status if dynamic', async () => {
    //   // ... logic to simulate different server states if applicable ...
    // });
  });
});
