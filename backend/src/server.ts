import express, { Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import componentRoutes from './routes/componentRoutes'; // Import the new router

const prisma = new PrismaClient();
const app = express();
const PORT = process.env.PORT || 3001; // Use 3001 to avoid conflict with potential React frontend later

// Middleware
app.use(express.json()); // Add middleware to parse JSON request bodies (good practice)

// Health Check Route
app.get('/api/v1/health', (req: Request, res: Response) => {
  res.status(200).json({ status: 'UP', timestamp: new Date().toISOString() });
});

// Component Routes
app.use('/api/v1/components', componentRoutes); // Use the component router with a base path

// Graceful shutdown
process.on('SIGINT', async () => {
  await prisma.$disconnect();
  console.log('Prisma client disconnected. Exiting.');
  process.exit(0);
});

process.on('SIGTERM', async () => {
  await prisma.$disconnect();
  console.log('Prisma client disconnected. Exiting.');
  process.exit(0);
});

async function main() {
  app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
    console.log(`Component routes available at /api/v1/components`);
  });
}

main()
  .catch(async (e) => {
    console.error("Error starting server:", e);
    await prisma.$disconnect();
    process.exit(1);
  });

export default app; // Export for potential testing
