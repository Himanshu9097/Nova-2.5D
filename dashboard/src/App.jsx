import React from 'react';
import { BenchmarkProvider } from './context/BenchmarkContext';
import Navbar from './components/Navbar';
import OverviewSection from './components/OverviewSection';
import RunBenchmarkSection from './components/RunBenchmarkSection';
import InputDataSection from './components/InputDataSection';
import PipelineSection from './components/PipelineSection';
import GridMethodsSection from './components/GridMethodsSection';
import VisualConceptSection from './components/VisualConceptSection';
import ComparisonSection from './components/ComparisonSection';
import MultiRunSection from './components/MultiRunSection';
import OutputMapSection from './components/OutputMapSection';
import ScalingSection from './components/ScalingSection';
import HistorySection from './components/HistorySection';
import ProjectStatusSection from './components/ProjectStatusSection';
import MetricsSection from './components/MetricsSection';
import FutureEvalSection from './components/FutureEvalSection';
import InsightsSection from './components/InsightsSection';
import Footer from './components/Footer';

export default function App() {
  return (
    <BenchmarkProvider>
      <div className="app-container">
        {/* Top sticky navigation & advisory strip */}
        <Navbar />

        {/* Main Content Area */}
        <main className="main-content">
          {/* Section 1: Overview & Active Telemetry KPIs */}
          <OverviewSection />

          {/* Section 2: Input-Driven Engine (Upload, Configure & Run Benchmark) */}
          <RunBenchmarkSection />

          {/* Section 3: Input Data & Active Point Cloud Breakdown */}
          <InputDataSection />

          {/* Section 4: Grid Representation Architectures (Uniform 0.5m vs Adaptive) */}
          <GridMethodsSection />

          {/* Section 5: Conceptual 2.5D Elevation Grid Model */}
          <VisualConceptSection />

          {/* Section 6: Head-to-Head Benchmark Performance Comparison */}
          <ComparisonSection />

          {/* Section 7: Run-by-Run Empirical Iteration Analysis */}
          <MultiRunSection />

          {/* Section 8: 2.5D Output Map Representation (Top-Down Generated Cells) */}
          <OutputMapSection />

          {/* Section 9: Point Cloud Size Scaling Analysis (5K - 50K Points) */}
          <ScalingSection />

          {/* Section 10: Persistent Benchmark History Archive */}
          <HistorySection />

          {/* Section 11: Processing & Architectural Evaluation Pipelines */}
          <PipelineSection />

          {/* Section 12: Engineering Status Matrix */}
          <ProjectStatusSection />

          {/* Section 13: Metrics Taxonomy ("What We Measure") */}
          <MetricsSection />

          {/* Section 14: Downstream CARLA Simulator & Sensor Integration Roadmap */}
          <FutureEvalSection />

          {/* Section 15: Research Insights & Empirical Baseline Synthesis */}
          <InsightsSection />
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </BenchmarkProvider>
  );
}
