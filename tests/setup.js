// Test setup file
require('dotenv').config({ path: '.env.test' });

// Set test environment variables
process.env.NODE_ENV = 'test';
process.env.PORT = '3002';
process.env.DATABASE_URL = 'postgresql://test:test@localhost:5432/azure_diagrams_test';

// Mock external services for testing
jest.mock('groq-sdk', () => {
  return {
    Groq: jest.fn().mockImplementation(() => ({
      chat: {
        completions: {
          create: jest.fn().mockResolvedValue({
            choices: [{
              message: {
                content: JSON.stringify({
                  elements: [
                    {
                      id: 'test-element',
                      type: 'azure-app-service',
                      text: 'Test App Service',
                      description: 'Test description',
                      x: 100,
                      y: 100,
                      width: 180,
                      height: 100,
                      color: '#0078d4'
                    }
                  ],
                  connections: [],
                  metadata: {
                    totalElements: 1,
                    totalConnections: 0,
                    detectedServices: ['azure-app-service']
                  }
                })
              }
            }]
          })
        }
      }
    }))
  };
});

// Global test timeout
jest.setTimeout(10000);
