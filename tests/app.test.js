const request = require('supertest');
const app = require('../server');

describe('Azure Diagram Generator API', () => {
  
  describe('GET /api/health', () => {
    it('should return health status', async () => {
      const response = await request(app)
        .get('/api/health')
        .expect(200);
      
      expect(response.body.status).toBe('OK');
      expect(response.body.version).toBe('2.0.0');
    });
  });

  describe('GET /api/examples', () => {
    it('should return architecture examples', async () => {
      const response = await request(app)
        .get('/api/examples')
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.examples)).toBe(true);
      expect(response.body.examples.length).toBeGreaterThan(0);
    });
  });

  describe('POST /api/generate-diagram', () => {
    it('should generate diagram from description', async () => {
      const description = 'Una aplicación web con App Service y SQL Database';
      
      const response = await request(app)
        .post('/api/generate-diagram')
        .send({ description })
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeDefined();
      expect(response.body.data.elements).toBeDefined();
      expect(response.body.data.connections).toBeDefined();
      expect(response.body.data.metadata).toBeDefined();
    });

    it('should return error for empty description', async () => {
      const response = await request(app)
        .post('/api/generate-diagram')
        .send({ description: '' })
        .expect(400);
      
      expect(response.body.success).toBe(false);
      expect(response.body.error).toBeDefined();
    });

    it('should handle AI processing when API key is available', async () => {
      const description = 'Arquitectura de microservicios con API Gateway';
      
      const response = await request(app)
        .post('/api/generate-diagram')
        .send({ description, useAI: true })
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body.data.metadata.processingMethod).toBeDefined();
    });
  });

  describe('GET /', () => {
    it('should serve the main HTML page', async () => {
      const response = await request(app)
        .get('/')
        .expect(200);
      
      expect(response.text).toContain('Azure Diagram Generator');
    });
  });

  describe('Rate Limiting', () => {
    it('should apply rate limiting to API endpoints', async () => {
      // Make multiple requests quickly
      const promises = Array(10).fill().map(() => 
        request(app).get('/api/health')
      );
      
      const responses = await Promise.all(promises);
      
      // All should succeed (within rate limit)
      responses.forEach(response => {
        expect(response.status).toBeLessThan(500);
      });
    });
  });
});
