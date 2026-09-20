"use client";

import * as React from "react";
import { Bar, BarChart, CartesianGrid, XAxis } from "recharts";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

const URGENCY_LABELS = { 1: "Critical", 2: "High", 3: "Moderate", 4: "Low" };

const chartConfig = {
  count: {
    label: "Patients",
    color: "var(--chart-1)",
  },
};

export function ChartBarInteractive({ patients = [] }) {
  const chartData = React.useMemo(() => {
    const counts = { 1: 0, 2: 0, 3: 0, 4: 0 };
    for (const p of patients) counts[p.urgency] = (counts[p.urgency] || 0) + 1;

    return Object.entries(counts).map(([urgency, count]) => ({
      urgency: URGENCY_LABELS[urgency],
      count,
    }));
  }, [patients]);

  return (
    <Card className="py-0">
      <CardHeader className="flex flex-col items-stretch border-b p-0 sm:flex-row">
        <div className="flex flex-1 flex-col justify-center gap-1 px-6 pt-4 pb-3 sm:py-0">
          <CardTitle>Patients by Urgency</CardTitle>
          <CardDescription>Currently admitted patients broken down by urgency level</CardDescription>
        </div>
      </CardHeader>

      <CardContent className="px-2 sm:p-6">
        <ChartContainer config={chartConfig} className="aspect-auto h-[250px] w-full">
          <BarChart accessibilityLayer data={chartData} margin={{ left: 12, right: 12 }}>
            <CartesianGrid vertical={false} />
            <XAxis dataKey="urgency" tickLine={false} axisLine={false} tickMargin={8} />
            <ChartTooltip content={<ChartTooltipContent className="w-[150px]" />} />
            <Bar dataKey="count" fill="var(--color-count)" />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}