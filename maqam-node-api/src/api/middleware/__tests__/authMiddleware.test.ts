import { Request, Response, NextFunction } from 'express';
import { apiKeyAuth } from '../authMiddleware';

describe('apiKeyAuth Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: NextFunction = jest.fn();
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    mockRequest = {
      header: jest.fn(),
    };
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn(),
    };
    nextFunction = jest.fn();
    originalEnv = { ...process.env }; // Backup original environment variables
  });

  afterEach(() => {
    process.env = originalEnv; // Restore original environment variables
    jest.clearAllMocks(); // Clear all mocks
  });

  it('should call next() if a valid API key is provided via X-API-Key header', () => {
    process.env.NODE_API_KEY = 'testkey';
    (mockRequest.header as jest.Mock).mockReturnValue('testkey');

    apiKeyAuth(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(nextFunction).toHaveBeenCalledTimes(1);
    expect(mockResponse.status).not.toHaveBeenCalled();
    expect(mockResponse.json).not.toHaveBeenCalled();
  });

  it('should return 401 if API key is missing', () => {
    (mockRequest.header as jest.Mock).mockReturnValue(undefined);

    apiKeyAuth(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(nextFunction).not.toHaveBeenCalled();
    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith({
      status: 'error',
      message: 'Unauthorized: API Key missing or invalid',
    });
  });

  it('should return 401 if an invalid API key is provided', () => {
    process.env.NODE_API_KEY = 'testkey';
    (mockRequest.header as jest.Mock).mockReturnValue('wrongkey');

    apiKeyAuth(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(nextFunction).not.toHaveBeenCalled();
    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith({
      status: 'error',
      message: 'Unauthorized: API Key missing or invalid',
    });
  });

  it('should use NODE_API_KEY environment variable for expected key', () => {
    process.env.NODE_API_KEY = 'envkey123';
    (mockRequest.header as jest.Mock).mockReturnValue('envkey123');

    apiKeyAuth(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(nextFunction).toHaveBeenCalledTimes(1);
  });

  it('should use fallback default API key if NODE_API_KEY is not set', () => {
    delete process.env.NODE_API_KEY; // Ensure NODE_API_KEY is not set
    const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
    (mockRequest.header as jest.Mock).mockReturnValue('supersecretkey'); // Default key

    apiKeyAuth(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(nextFunction).toHaveBeenCalledTimes(1);
    expect(consoleWarnSpy).toHaveBeenCalledWith('Warning: NODE_API_KEY is not set. Using default API key for development.');
    consoleWarnSpy.mockRestore();
  });
  
  it('should return 401 if NODE_API_KEY is not set and an invalid key is provided', () => {
    delete process.env.NODE_API_KEY;
    const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
    (mockRequest.header as jest.Mock).mockReturnValue('wrongkey');

    apiKeyAuth(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(nextFunction).not.toHaveBeenCalled();
    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith({
      status: 'error',
      message: 'Unauthorized: API Key missing or invalid',
    });
    expect(consoleWarnSpy).toHaveBeenCalledWith('Warning: NODE_API_KEY is not set. Using default API key for development.');
    consoleWarnSpy.mockRestore();
  });
});
