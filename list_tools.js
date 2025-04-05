const { spawn } = require('child_process');
const path = require('path');

// Path to servers
const testingServerPath = path.resolve(__dirname, 'mcp_servers/testing-integration-server/build/index.js');
const contextServerPath = path.resolve(__dirname, 'mcp_servers/context-management-server/build/index.js');

// Function to list tools for a server
async function listTools(serverPath, serverName) {
  return new Promise((resolve, reject) => {
    console.log(`\n--- Listing tools for ${serverName} ---`);
    
    const server = spawn('node', [serverPath], {
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    let stdout = '';
    let stderr = '';
    
    server.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    server.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    server.on('close', (code) => {
      console.log(`Server exited with code ${code}`);
      if (stderr) {
        console.log(`${serverName} stderr (truncated):`, stderr.substring(0, 500) + '...');
      }
      
      try {
        // Try to parse JSON from stdout
        const responseLines = stdout.trim().split('\n');
        if (responseLines.length === 0) {
          console.log('No response received');
          resolve([]);
          return;
        }
        
        // Try to parse each line as JSON
        for (const line of responseLines) {
          try {
            const response = JSON.parse(line);
            if (response && !response.error && response.result && response.result.tools) {
              console.log(`Found ${response.result.tools.length} tools for ${serverName}`);
              console.log('Tool names:');
              response.result.tools.forEach(tool => {
                console.log(`- ${tool.name}${tool.description ? ': ' + tool.description : ''}`);
              });
              resolve(response.result.tools);
              return;
            } else if (response && response.error) {
              console.log('Error response:', response.error);
            }
          } catch (e) {
            // Not valid JSON, skip
          }
        }
        
        console.log('No valid JSON response found in:', stdout);
        resolve([]);
      } catch (e) {
        console.error('Error processing response:', e);
        console.log('Raw stdout:', stdout);
        resolve([]);
      }
    });
    
    // MCP format for listing tools
    const request = {
      jsonrpc: "2.0",
      method: "listTools",
      id: "1",
      params: {}
    };
    
    server.stdin.write(JSON.stringify(request) + '\n');
    server.stdin.end();
  });
}

// Run the tests
async function main() {
  try {
    // First list tools for the testing server
    await listTools(testingServerPath, 'Testing Integration Server');
    
    // Then list tools for the context management server
    await listTools(contextServerPath, 'Context Management Server');
    
    console.log('\nTool listing completed.');
  } catch (error) {
    console.error('Error:', error);
  }
}

// Run the tests
main(); 