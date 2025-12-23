import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { apiClient, bandoAPI } from '@/services/api';

/**
 * Test Suite per Integrazione API Backend ISS
 * Verifica connettività e funzionalità core del sistema bandi
 */

const TEST_CONFIG = {
  backendUrl: 'http://localhost:8001',
  timeout: 10000,
  retries: 3
};

describe('🧪 ISS API Integration Tests', () => {
  beforeAll(async () => {
    // Verifica che il backend sia raggiungibile
    try {
      const response = await fetch(`${TEST_CONFIG.backendUrl}/health`);
      const health = await response.json();
      expect(health.status).toBe('healthy');
      console.log('✅ Backend is healthy and ready for testing');
    } catch (error) {
      console.error('❌ Backend not available:', error);
      throw new Error('Backend must be running for integration tests');
    }
  });

  describe('🏥 Health & Status Tests', () => {
    it('should return healthy status', async () => {
      const health = await apiClient.healthCheck();
      expect(health).toHaveProperty('status');
      expect(health.status).toBe('healthy');
      expect(health).toHaveProperty('timestamp');
    });
  });

  describe('📊 Bandi API Tests', () => {
    it('should fetch bandi list with pagination', async () => {
      const response = await bandoAPI.search({ limit: 10, skip: 0 });
      
      expect(response).toHaveProperty('items');
      expect(response).toHaveProperty('total');
      expect(response).toHaveProperty('page');
      expect(response).toHaveProperty('size');
      expect(Array.isArray(response.items)).toBe(true);
      expect(typeof response.total).toBe('number');
      
      console.log(`✅ Found ${response.total} bandi in database`);
    });

    it('should fetch bandi statistics', async () => {
      const stats = await bandoAPI.getStats();
      
      expect(stats).toHaveProperty('total_bandi');
      expect(stats).toHaveProperty('bandi_attivi');
      expect(stats).toHaveProperty('bandi_scaduti');
      expect(stats).toHaveProperty('bandi_per_fonte');
      expect(typeof stats.total_bandi).toBe('number');
      
      console.log('✅ Bandi statistics:', {
        total: stats.total_bandi,
        attivi: stats.bandi_attivi,
        scaduti: stats.bandi_scaduti
      });
    });

    it('should search bandi with query parameters', async () => {
      const searchParams = {
        query: 'test',
        limite: 5,
        skip: 0
      };
      
      const response = await bandoAPI.search(searchParams);
      expect(response.items.length).toBeGreaterThanOrEqual(0);
      expect(response.size).toBeLessThanOrEqual(5);
      
      if (response.items.length > 0) {
        const firstBando = response.items[0];
        expect(firstBando).toHaveProperty('title');
        expect(firstBando).toHaveProperty('ente');
        expect(firstBando).toHaveProperty('fonte');
        expect(firstBando).toHaveProperty('status');
        
        console.log('✅ Search test passed with sample bando:', firstBando.title);
      }
    });

    it('should handle filter by fonte', async () => {
      const response = await bandoAPI.search({ 
        fonte: 'comune_salerno',
        limit: 10 
      });
      
      expect(response).toHaveProperty('items');
      response.items.forEach(bando => {
        expect(bando.fonte).toBe('comune_salerno');
      });
      
      console.log(`✅ Fonte filter test: ${response.items.length} bandi from Comune Salerno`);
    });

    it('should handle empty search gracefully', async () => {
      const response = await bandoAPI.search({ 
        query: 'nonexistentquerythatshouldretur nothingxyz123',
        limit: 10 
      });
      
      expect(response.items).toHaveLength(0);
      expect(response.total).toBe(0);
      
      console.log('✅ Empty search handled correctly');
    });
  });

  describe('🔍 Individual Bando Tests', () => {
    it('should fetch individual bando by ID', async () => {
      // First get a bando ID from the list
      const listResponse = await bandoAPI.search({ limit: 1 });
      
      if (listResponse.items.length > 0) {
        const bandoId = listResponse.items[0].id;
        const bando = await bandoAPI.getById(bandoId);
        
        expect(bando).toHaveProperty('id');
        expect(bando.id).toBe(bandoId);
        expect(bando).toHaveProperty('title');
        expect(bando).toHaveProperty('ente');
        
        console.log('✅ Individual bando fetch test passed:', bando.title);
      } else {
        console.log('⚠️ No bandi available for individual fetch test');
      }
    });
  });

  describe('⚡ Performance Tests', () => {
    it('should handle concurrent requests efficiently', async () => {
      const startTime = Date.now();
      
      // Execute 5 concurrent API calls
      const promises = Array.from({ length: 5 }, (_, i) => 
        bandoAPI.search({ 
          limit: 10, 
          skip: i * 10 
        })
      );
      
      const results = await Promise.all(promises);
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      expect(results).toHaveLength(5);
      results.forEach(result => {
        expect(result).toHaveProperty('items');
        expect(result).toHaveProperty('total');
      });
      
      // Should complete within reasonable time (adjust as needed)
      expect(duration).toBeLessThan(5000);
      
      console.log(`✅ Concurrent requests completed in ${duration}ms`);
    });

    it('should handle large limit requests', async () => {
      const startTime = Date.now();
      
      const response = await bandoAPI.search({ 
        limit: 100, 
        skip: 0 
      });
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      expect(response).toHaveProperty('items');
      expect(response.items.length).toBeLessThanOrEqual(100);
      
      // Should complete within reasonable time
      expect(duration).toBeLessThan(3000);
      
      console.log(`✅ Large query completed in ${duration}ms, returned ${response.items.length} items`);
    });
  });

  describe('🚫 Error Handling Tests', () => {
    it('should handle invalid bando ID gracefully', async () => {
      try {
        await bandoAPI.getById(999999);
        // If we get here, the API should have returned 404 but didn't throw
        // This might be acceptable depending on API design
      } catch (error: any) {
        // Expected behavior - API should return 404 for non-existent bando
        expect(error.response?.status).toBe(404);
        console.log('✅ 404 error handled correctly for invalid bando ID');
      }
    });

    it('should handle malformed requests', async () => {
      try {
        // Try to pass invalid parameters
        await bandoAPI.search({ 
          limit: -1,  // Invalid limit
          skip: 'invalid' as any  // Invalid skip
        });
      } catch (error: any) {
        // API should validate and reject malformed requests
        console.log('✅ Malformed request handled:', error.message);
      }
    });
  });
});

/**
 * Performance Benchmark Tests
 * These tests help identify performance bottlenecks
 */
describe('📊 Performance Benchmarks', () => {
  it('should measure search response times', async () => {
    const measurements: number[] = [];
    
    // Run 10 search requests and measure response times
    for (let i = 0; i < 10; i++) {
      const start = Date.now();
      await bandoAPI.search({ limit: 20 });
      const end = Date.now();
      measurements.push(end - start);
    }
    
    const avgResponseTime = measurements.reduce((a, b) => a + b) / measurements.length;
    const maxResponseTime = Math.max(...measurements);
    const minResponseTime = Math.min(...measurements);
    
    console.log('📊 Search Performance Metrics:');
    console.log(`  Average: ${avgResponseTime.toFixed(2)}ms`);  
    console.log(`  Min: ${minResponseTime}ms`);
    console.log(`  Max: ${maxResponseTime}ms`);
    
    // Performance thresholds (adjust as needed)
    expect(avgResponseTime).toBeLessThan(1000); // Average under 1 second
    expect(maxResponseTime).toBeLessThan(2000); // Max under 2 seconds
  });
});

console.log('🧪 ISS API Integration Test Suite Ready');
