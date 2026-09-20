"use client";

import * as React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  XAxis,
} from "recharts";

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

const chartData = [
  { date: "2026-09-01", desktop: 222, mobile: 150 },
  { date: "2026-09-02", desktop: 97, mobile: 180 },
  { date: "2026-09-03", desktop: 167, mobile: 120 },
  { date: "2026-09-04", desktop: 242, mobile: 260 },
  { date: "2026-09-05", desktop: 373, mobile: 290 },
  { date: "2026-09-06", desktop: 301, mobile: 340 },
  { date: "2026-09-07", desktop: 245, mobile: 180 },
  { date: "2026-09-08", desktop: 409, mobile: 320 },
  { date: "2026-09-09", desktop: 159, mobile: 110 },
  { date: "2026-09-10", desktop: 261, mobile: 190 },
  { date: "2026-09-11", desktop: 327, mobile: 350 },
  { date: "2026-09-12", desktop: 292, mobile: 210 },
  { date: "2026-09-13", desktop: 342, mobile: 380 },
  { date: "2026-09-14", desktop: 137, mobile: 220 },
  { date: "2026-09-15", desktop: 120, mobile: 170 },
  { date: "2026-09-16", desktop: 138, mobile: 190 },
  { date: "2026-09-17", desktop: 446, mobile: 360 },
  { date: "2026-09-18", desktop: 364, mobile: 410 },
  { date: "2026-09-19", desktop: 243, mobile: 180 },
  { date: "2026-09-20", desktop: 89, mobile: 150 },
];

const chartConfig = {
  desktop: {
    label: "Outpatients",
    color: "var(--chart-2)",
  },
  mobile: {
    label: "Inpatients",
    color: "var(--chart-1)",
  },
};

export function ChartBarInteractive() {
  const [activeChart, setActiveChart] = React.useState("desktop");

  const total = React.useMemo(
    () => ({
      desktop: chartData.reduce(
        (acc, curr) => acc + curr.desktop,
        0
      ),
      mobile: chartData.reduce(
        (acc, curr) => acc + curr.mobile,
        0
      ),
    }),
    []
  );

  return (
    <Card className="py-0">
      <CardHeader className="flex flex-col items-stretch border-b p-0 sm:flex-row">
        <div className="flex flex-1 flex-col justify-center gap-1 px-6 pt-4 pb-3 sm:py-0">
          <CardTitle>Patient Activity</CardTitle>

          <CardDescription>
            Patient admissions and visits over the last 20 days
          </CardDescription>
        </div>

        <div className="flex">
          {["desktop", "mobile"].map((key) => {
            const chart = key;

            return (
              <button
                key={chart}
                data-active={activeChart === chart}
                className="relative z-30 flex flex-1 flex-col justify-center gap-1 border-t px-6 py-4 text-left even:border-l data-[active=true]:bg-muted/50 sm:border-t-0 sm:border-l sm:px-8 sm:py-6"
                onClick={() => setActiveChart(chart)}
              >
                <span className="text-xs text-muted-foreground">
                  {chartConfig[chart].label}
                </span>

                <span className="text-lg leading-none font-bold sm:text-3xl">
                  {total[chart].toLocaleString()}
                </span>
              </button>
            );
          })}
        </div>
      </CardHeader>

      <CardContent className="px-2 sm:p-6">
        <ChartContainer
          config={chartConfig}
          className="aspect-auto h-[250px] w-full"
        >
          <BarChart
            accessibilityLayer
            data={chartData}
            margin={{
              left: 12,
              right: 12,
            }}
          >
            <CartesianGrid vertical={false} />

            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={32}
              tickFormatter={(value) => {
                const date = new Date(value);

                return date.toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                });
              }}
            />

            <ChartTooltip
              content={
                <ChartTooltipContent
                  className="w-[150px]"
                  nameKey="views"
                  labelFormatter={(value) => {
                    return new Date(value).toLocaleDateString(
                      "en-US",
                      {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      }
                    );
                  }}
                />
              }
            />

            <Bar
              dataKey={activeChart}
              fill={`var(--color-${activeChart})`}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}