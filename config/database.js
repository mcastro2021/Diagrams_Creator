const { Pool } = require('pg');

// Database configuration
const dbConfig = {
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
  max: 20, // Maximum number of clients in the pool
  idleTimeoutMillis: 30000, // Close idle clients after 30 seconds
  connectionTimeoutMillis: 2000, // Return an error after 2 seconds if connection could not be established
};

// Create connection pool
const pool = new Pool(dbConfig);

// Handle pool errors
pool.on('error', (err) => {
  console.error('Unexpected error on idle client', err);
  process.exit(-1);
});

// Test database connection
async function testConnection() {
  try {
    const client = await pool.connect();
    const result = await client.query('SELECT NOW()');
    console.log('✅ Database connected successfully:', result.rows[0].now);
    client.release();
    return true;
  } catch (err) {
    console.error('❌ Database connection failed:', err.message);
    return false;
  }
}

// Initialize database tables
async function initializeDatabase() {
  try {
    const client = await pool.connect();
    
    // Check if tables exist
    const result = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      AND table_name IN ('users', 'diagrams', 'diagram_versions', 'diagram_collaborations', 'user_sessions', 'api_usage')
    `);
    
    const existingTables = result.rows.map(row => row.table_name);
    const requiredTables = ['users', 'diagrams', 'diagram_versions', 'diagram_collaborations', 'user_sessions', 'api_usage'];
    const missingTables = requiredTables.filter(table => !existingTables.includes(table));
    
    if (missingTables.length > 0) {
      console.log('⚠️ Missing database tables:', missingTables);
      console.log('Please run the schema.sql file to create the required tables.');
    } else {
      console.log('✅ All required database tables exist');
    }
    
    client.release();
    return true;
  } catch (err) {
    console.error('❌ Database initialization failed:', err.message);
    return false;
  }
}

module.exports = {
  pool,
  testConnection,
  initializeDatabase
};
