"use client";

import { useEffect, useState } from "react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

const backend_url = process.env.NEXT_PUBLIC_BACKEND_URL;

export default function ResourcesPage() {
  const [data, setData] = useState(null);

  const fetchResources = async () => {
    const res = await fetch(`${backend_url}/api/patients/resources/status`, {
      cache: "no-store",
    });
    if (res.ok) setData(await res.json());
  };

  useEffect(() => {
    fetchResources();
    const interval = setInterval(fetchResources, 3000);
    return () => clearInterval(interval);
  }, []);

  if (!data) {
    return <div className="p-6 text-muted-foreground">Loading resources...</div>;
  }

  return (
    <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Hospital Resources</h1>
        <Badge variant="outline">{data.clock_time}</Badge>
      </div>

      {/* Beds / ICU / Nurses */}
      <div className="grid grid-cols-1 gap-4 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
        {Object.entries(data.resources).map(([name, { free, capacity }]) => {
          const used = capacity - free;
          const pct = capacity ? (used / capacity) * 100 : 0;

          return (
            <Card key={name}>
              <CardHeader>
                <CardDescription className="capitalize">
                  {name.replace("_", " ")}
                </CardDescription>
                <CardTitle className="text-2xl font-semibold tabular-nums">
                  {free} / {capacity}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Progress value={pct} />
                <p className="mt-2 text-xs text-muted-foreground">
                  {free} free
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Doctors */}
      <Card>
        <CardHeader>
          <CardTitle>Doctors</CardTitle>
          <CardDescription>
            {data.doctors.available} available / {data.doctors.total} total,{" "}
            {data.doctors.busy} busy
          </CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-3 @xl/main:grid-cols-3">
          {Object.entries(data.doctors.by_specialty).map(([spec, s]) => (
            <div
              key={spec}
              className="flex items-center justify-between rounded-md border px-3 py-2 text-sm"
            >
              <span>{spec}</span>
              <Badge variant="outline">
                {s.available}/{s.total}
              </Badge>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardDescription>Patients Waiting for Resources</CardDescription>
          <CardTitle className="text-2xl font-semibold">
            {data.waiting_count}
          </CardTitle>
        </CardHeader>
      </Card>
    </div>
  );
}