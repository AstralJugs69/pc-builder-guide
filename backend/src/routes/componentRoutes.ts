import { Router, Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';

const router = Router();
// It's often better practice to pass the prisma client instance rather than creating a new one
// We will modify server.ts to pass it via middleware or dependency injection pattern later if needed.
// For now, creating a new instance here is simple, but less ideal for connection pooling.
// Let's instantiate it directly in the main server file and find a way to pass it.
// --- Reverting this thought: For simplicity in this step, let's keep the instance here.
// We can refactor later if needed for connection management. ---
const prisma = new PrismaClient();

// GET /api/v1/components/cpus - Retrieve all CPUs
router.get('/cpus', async (req: Request, res: Response) => {
  try {
    const cpus = await prisma.cpu.findMany();
    res.status(200).json(cpus);
  } catch (error) {
    console.error("Error fetching CPUs:", error);
    res.status(500).json({ error: 'Failed to retrieve CPUs' });
  }
});

// GET /api/v1/components/gpus - Retrieve all GPUs
router.get('/gpus', async (req: Request, res: Response) => {
  try {
    const gpus = await prisma.gpu.findMany();
    res.status(200).json(gpus);
  } catch (error) {
    console.error("Error fetching GPUs:", error);
    res.status(500).json({ error: 'Failed to retrieve GPUs' });
  }
});

export default router;
