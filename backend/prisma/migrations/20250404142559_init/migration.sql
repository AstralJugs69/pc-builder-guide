-- CreateTable
CREATE TABLE "cpus" (
    "cpu_id" SERIAL NOT NULL,
    "model_name" TEXT NOT NULL,
    "manufacturer" TEXT,
    "core_count" INTEGER,
    "thread_count" INTEGER,
    "base_clock_ghz" DECIMAL(4,2),
    "boost_clock_ghz" DECIMAL(4,2),
    "socket" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "cpus_pkey" PRIMARY KEY ("cpu_id")
);

-- CreateTable
CREATE TABLE "gpus" (
    "gpu_id" SERIAL NOT NULL,
    "model_name" TEXT NOT NULL,
    "manufacturer" TEXT,
    "memory_gb" INTEGER,
    "memory_type" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "gpus_pkey" PRIMARY KEY ("gpu_id")
);

-- CreateTable
CREATE TABLE "games" (
    "game_id" SERIAL NOT NULL,
    "title" TEXT NOT NULL,
    "release_year" INTEGER,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "games_pkey" PRIMARY KEY ("game_id")
);

-- CreateTable
CREATE TABLE "benchmarks" (
    "benchmark_id" SERIAL NOT NULL,
    "cpuId" INTEGER,
    "gpuId" INTEGER NOT NULL,
    "gameId" INTEGER NOT NULL,
    "resolution" TEXT NOT NULL,
    "graphics_settings" TEXT NOT NULL,
    "average_fps" DECIMAL(6,2) NOT NULL,
    "minimum_fps" DECIMAL(6,2),
    "percentile_1_fps" DECIMAL(6,2),
    "data_source_url" TEXT NOT NULL,
    "scraped_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "benchmarks_pkey" PRIMARY KEY ("benchmark_id")
);

-- CreateIndex
CREATE UNIQUE INDEX "cpus_model_name_key" ON "cpus"("model_name");

-- CreateIndex
CREATE UNIQUE INDEX "gpus_model_name_key" ON "gpus"("model_name");

-- CreateIndex
CREATE UNIQUE INDEX "games_title_key" ON "games"("title");

-- CreateIndex
CREATE UNIQUE INDEX "benchmarks_uniqueness_constraint" ON "benchmarks"("gpuId", "gameId", "resolution", "graphics_settings", "data_source_url", "cpuId");

-- AddForeignKey
ALTER TABLE "benchmarks" ADD CONSTRAINT "benchmarks_cpuId_fkey" FOREIGN KEY ("cpuId") REFERENCES "cpus"("cpu_id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "benchmarks" ADD CONSTRAINT "benchmarks_gpuId_fkey" FOREIGN KEY ("gpuId") REFERENCES "gpus"("gpu_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "benchmarks" ADD CONSTRAINT "benchmarks_gameId_fkey" FOREIGN KEY ("gameId") REFERENCES "games"("game_id") ON DELETE RESTRICT ON UPDATE CASCADE;
