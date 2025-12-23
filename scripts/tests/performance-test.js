#!/usr/bin/env node

/**
 * 🚀 ISS SISTEMA BANDI - PERFORMANCE TEST SUITE
 * Test automatizzati per performance su dataset 500+ bandi
 * 
 * Requirements:
 * - Node.js 18+
 * - Backend running on localhost:8000
 * - Database populated with test data
 */

const axios = require('axios');
const { performance } = require('perf_hooks');

const CONFIG = {
  BASE_URL: 'http://localhost:8000/api/v1',
  TEST_ITERATIONS: 100,
  CONCURRENT_USERS: 50,
  TARGET_RESPONSE_TIME: 2000, // 2 seconds
  TARGET_THROUGHPUT: 100, // requests per second
  DATASET_SIZE: 500
};

class PerformanceTestSuite {
  constructor() {
    this.results = {
      searchTests: [],
      concurrentTests: [],
      stressTests: [],
      memoryUsage: [],
      errors: []
    };
  }

  async runFullSuite() {
    console.log('🚀 Starting ISS Bandi Performance Test Suite...\n');
    
    try {
      // 1. Pre-test checks
      await this.preTestChecks();
      
      // 2. Basic performance tests
      await this.runSearchPerformanceTests();
      
      // 3. Concurrent user tests
      await this.runConcurrentUserTests();
      
      // 4. Stress tests
      await this.runStressTests();
      
      // 5. Memory and resource tests
      await this.runResourceTests();
      
      // 6. Generate report
      this.generateReport();
      
    } catch (error) {
      console.error('❌ Test suite failed:', error.message);
      process.exit(1);
    }
  }

  async preTestChecks() {
    console.log('🔍 Pre-test checks...');
    
    // Check backend health
    try {
      const healthCheck = await axios.get(`${CONFIG.BASE_URL.replace('/api/v1', '')}/health`);
      console.log('✅ Backend is healthy');
    } catch (error) {
      throw new Error(`Backend not accessible: ${error.message}`);
    }

    // Check bandi endpoint and count
    try {
      const bandiCount = await axios.get(`${CONFIG.BASE_URL}/bandi/stats`);
      const totalBandi = bandiCount.data.total_bandi;
      
      if (totalBandi < CONFIG.DATASET_SIZE) {
        console.log(`⚠️  Warning: Only ${totalBandi} bandi in database, expected ${CONFIG.DATASET_SIZE}+`);
      } else {
        console.log(`✅ Dataset ready: ${totalBandi} bandi available`);
      }
    } catch (error) {
      throw new Error(`Cannot access bandi stats: ${error.message}`);
    }

    console.log('');
  }

  async runSearchPerformanceTests() {
    console.log('📊 Running search performance tests...');
    
    const searchQueries = [
      { query: 'giovani' },
      { query: 'inclusione sociale' },
      { query: 'formazione' },
      { fonte: 'comune_salerno' },
      { fonte: 'regione_campania' },
      { limit: 50 },
      { limit: 100 },
      { query: 'ambiente', limite: 20 }
    ];

    for (let i = 0; i < CONFIG.TEST_ITERATIONS; i++) {
      const randomQuery = searchQueries[i % searchQueries.length];
      
      const startTime = performance.now();
      try {
        const response = await axios.get(`${CONFIG.BASE_URL}/bandi/`, {
          params: randomQuery,
          timeout: 10000
        });
        
        const endTime = performance.now();
        const responseTime = endTime - startTime;
        
        this.results.searchTests.push({
          iteration: i + 1,
          query: randomQuery,
          responseTime,
          itemsReturned: response.data.items.length,
          totalFound: response.data.total,
          success: true
        });

        if (responseTime > CONFIG.TARGET_RESPONSE_TIME) {
          console.log(`⚠️  Slow response (${responseTime.toFixed(2)}ms) for query:`, randomQuery);
        }

      } catch (error) {
        this.results.errors.push({
          test: 'search',
          iteration: i + 1,
          query: randomQuery,
          error: error.message
        });
      }

      // Progress indicator
      if ((i + 1) % 10 === 0) {
        process.stdout.write(`${i + 1}/${CONFIG.TEST_ITERATIONS} `);
      }
    }
    
    console.log('\n✅ Search performance tests completed\n');
  }

  async runConcurrentUserTests() {
    console.log('👥 Running concurrent user tests...');
    
    const concurrentPromises = [];
    
    for (let user = 0; user < CONFIG.CONCURRENT_USERS; user++) {
      const userTestPromise = this.simulateUserSession(user);
      concurrentPromises.push(userTestPromise);
    }

    const startTime = performance.now();
    const results = await Promise.allSettled(concurrentPromises);
    const endTime = performance.now();
    
    const successful = results.filter(r => r.status === 'fulfilled').length;
    const failed = results.filter(r => r.status === 'rejected').length;
    
    this.results.concurrentTests.push({
      concurrentUsers: CONFIG.CONCURRENT_USERS,
      totalTime: endTime - startTime,
      successful,
      failed,
      successRate: (successful / CONFIG.CONCURRENT_USERS) * 100
    });

    console.log(`✅ Concurrent test: ${successful}/${CONFIG.CONCURRENT_USERS} users successful`);
    console.log(`   Total time: ${(endTime - startTime).toFixed(2)}ms\n`);
  }

  async simulateUserSession(userId) {
    const userActions = [
      () => axios.get(`${CONFIG.BASE_URL}/bandi/`, { params: { limit: 20 } }),
      () => axios.get(`${CONFIG.BASE_URL}/bandi/stats`),
      () => axios.get(`${CONFIG.BASE_URL}/bandi/`, { params: { query: 'test' } }),
      () => axios.get(`${CONFIG.BASE_URL}/bandi/`, { params: { fonte: 'comune_salerno' } })
    ];

    const sessionResults = [];
    
    for (const action of userActions) {
      const startTime = performance.now();
      try {
        await action();
        const endTime = performance.now();
        sessionResults.push({
          userId,
          responseTime: endTime - startTime,
          success: true
        });
      } catch (error) {
        sessionResults.push({
          userId,
          error: error.message,
          success: false
        });
      }
    }

    return sessionResults;
  }

  async runStressTests() {
    console.log('🔥 Running stress tests...');
    
    // Test with increasing load
    const loadLevels = [10, 25, 50, 100, 150];
    
    for (const load of loadLevels) {
      console.log(`  Testing with ${load} concurrent requests...`);
      
      const startTime = performance.now();
      const promises = Array.from({ length: load }, () => 
        axios.get(`${CONFIG.BASE_URL}/bandi/`, { 
          params: { limit: 20 },
          timeout: 15000 
        })
      );

      try {
        const results = await Promise.allSettled(promises);
        const endTime = performance.now();
        
        const successful = results.filter(r => r.status === 'fulfilled').length;
        const totalTime = endTime - startTime;
        const throughput = (successful / totalTime) * 1000; // requests per second

        this.results.stressTests.push({
          concurrentRequests: load,
          successful,
          failed: load - successful,
          totalTime,
          throughput,
          averageResponseTime: totalTime / load
        });

        console.log(`    ✅ ${successful}/${load} successful, ${throughput.toFixed(2)} req/sec`);

      } catch (error) {
        console.log(`    ❌ Stress test failed at ${load} concurrent requests`);
        this.results.errors.push({
          test: 'stress',
          load,
          error: error.message
        });
      }
    }
    
    console.log('✅ Stress tests completed\n');
  }

  async runResourceTests() {
    console.log('💾 Running resource utilization tests...');
    
    // Monitor memory usage during intensive operations
    const initialMemory = process.memoryUsage();
    
    // Run memory-intensive operations
    for (let i = 0; i < 50; i++) {
      await axios.get(`${CONFIG.BASE_URL}/bandi/`, { 
        params: { limit: 100 } 
      });
      
      if (i % 10 === 0) {
        const currentMemory = process.memoryUsage();
        this.results.memoryUsage.push({
          iteration: i,
          heapUsed: currentMemory.heapUsed,
          heapTotal: currentMemory.heapTotal,
          external: currentMemory.external
        });
      }
    }

    const finalMemory = process.memoryUsage();
    
    console.log('✅ Resource tests completed');
    console.log(`   Memory delta: ${((finalMemory.heapUsed - initialMemory.heapUsed) / 1024 / 1024).toFixed(2)} MB\n`);
  }

  generateReport() {
    console.log('📊 PERFORMANCE TEST REPORT');
    console.log('=' .repeat(50));
    
    // Search Performance Stats
    if (this.results.searchTests.length > 0) {
      const searchTimes = this.results.searchTests.map(t => t.responseTime);
      const avgSearchTime = searchTimes.reduce((a, b) => a + b) / searchTimes.length;
      const maxSearchTime = Math.max(...searchTimes);
      const minSearchTime = Math.min(...searchTimes);
      const p95SearchTime = this.percentile(searchTimes, 95);
      
      console.log('\n🔍 SEARCH PERFORMANCE:');
      console.log(`   Average response time: ${avgSearchTime.toFixed(2)}ms`);
      console.log(`   Min response time: ${minSearchTime.toFixed(2)}ms`);
      console.log(`   Max response time: ${maxSearchTime.toFixed(2)}ms`);
      console.log(`   95th percentile: ${p95SearchTime.toFixed(2)}ms`);
      console.log(`   Target compliance: ${avgSearchTime < CONFIG.TARGET_RESPONSE_TIME ? '✅' : '❌'}`);
    }

    // Concurrent User Stats  
    if (this.results.concurrentTests.length > 0) {
      const concurrentTest = this.results.concurrentTests[0];
      console.log('\n👥 CONCURRENT USER PERFORMANCE:');
      console.log(`   Concurrent users: ${concurrentTest.concurrentUsers}`);
      console.log(`   Success rate: ${concurrentTest.successRate.toFixed(2)}%`);
      console.log(`   Total test time: ${concurrentTest.totalTime.toFixed(2)}ms`);
    }

    // Stress Test Stats
    if (this.results.stressTests.length > 0) {
      const maxThroughput = Math.max(...this.results.stressTests.map(t => t.throughput));
      const maxSuccessfulLoad = Math.max(...this.results.stressTests
        .filter(t => t.failed === 0)
        .map(t => t.concurrentRequests)
      );
      
      console.log('\n🔥 STRESS TEST RESULTS:');
      console.log(`   Maximum throughput: ${maxThroughput.toFixed(2)} req/sec`);
      console.log(`   Maximum stable load: ${maxSuccessfulLoad} concurrent requests`);
      console.log(`   Target throughput: ${maxThroughput >= CONFIG.TARGET_THROUGHPUT ? '✅' : '❌'}`);
    }

    // Error Summary
    if (this.results.errors.length > 0) {
      console.log('\n❌ ERRORS ENCOUNTERED:');
      this.results.errors.forEach((error, index) => {
        console.log(`   ${index + 1}. ${error.test}: ${error.error}`);
      });
    } else {
      console.log('\n✅ NO ERRORS ENCOUNTERED');
    }

    // Overall Assessment
    const searchPerformanceGood = this.results.searchTests.length > 0 && 
      (this.results.searchTests.reduce((a, b) => a + b.responseTime, 0) / this.results.searchTests.length) < CONFIG.TARGET_RESPONSE_TIME;
    
    const concurrentPerformanceGood = this.results.concurrentTests.length > 0 && 
      this.results.concurrentTests[0].successRate > 95;
    
    const lowErrorRate = this.results.errors.length < 5;

    console.log('\n🏆 OVERALL ASSESSMENT:');
    console.log(`   Search Performance: ${searchPerformanceGood ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`   Concurrent Performance: ${concurrentPerformanceGood ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`   Error Rate: ${lowErrorRate ? '✅ PASS' : '❌ FAIL'}`);
    
    const overallPass = searchPerformanceGood && concurrentPerformanceGood && lowErrorRate;
    console.log(`\n🎯 PRODUCTION READY: ${overallPass ? '✅ YES' : '❌ NO'}`);
    
    if (!overallPass) {
      console.log('\n⚠️  RECOMMENDATIONS:');
      if (!searchPerformanceGood) console.log('   - Optimize search query performance');
      if (!concurrentPerformanceGood) console.log('   - Improve concurrent user handling');  
      if (!lowErrorRate) console.log('   - Fix error conditions');
    }

    console.log('\n' + '='.repeat(50));
  }

  percentile(arr, p) {
    const sorted = arr.slice().sort((a, b) => a - b);
    const index = Math.ceil((p / 100) * sorted.length) - 1;
    return sorted[index];
  }
}

// Run the performance test suite
if (require.main === module) {
  const testSuite = new PerformanceTestSuite();
  testSuite.runFullSuite().catch(error => {
    console.error('Performance test suite failed:', error);
    process.exit(1);
  });
}

module.exports = PerformanceTestSuite;
