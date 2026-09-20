"use client";

import { useEffect, useRef, useState } from "react";

import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const backend_url = process.env.NEXT_PUBLIC_BACKEND_URL;

export default function DiagnosesPage() {
  const [patients, setPatients] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const simState = useRef({}); // id -> { startedAt }

  const fetchPatients = async () => {
    const res = await fetch(`${backend_url}/api/patients/all`, { cache: "no-store" });
    const data = await res.json();

    for (const p of data.patients || []) {
      if (!simState.current[p.id]) {
        simState.current[p.id] = { startedAt: Date.now() };
      }
    }

    setPatients(data.patients || []);
    setLoading(false);
  };

  useEffect(() => {
    fetchPatients();
    const poll = setInterval(fetchPatients, 5000);
    const tick = setInterval(() => setPatients((p) => [...p]), 500); // force rerender for progress bars
    return () => {
      clearInterval(poll);
      clearInterval(tick);
    };
  }, []);

const getStatus = (p) => ({
  label: p.status,
  pct: p.end ? 100 : p.start ? Math.min(99, ((hospital_clock_estimate - p.start) / p.duration) * 100) : 0,
});

  const filtered = patients.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-1 flex-col gap-4 p-4 lg:p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Diagnosis Status</h1>
        <Input
          placeholder="Search patient..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
      </div>

      <div className="overflow-hidden rounded-lg border">
        <Table>
          <TableHeader className="bg-muted">
            <TableRow>
              <TableHead>Patient</TableHead>
              <TableHead>Diagnosis</TableHead>
              <TableHead>Urgency</TableHead>
              <TableHead>Wait</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-40">Progress</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : filtered.length ? (
              filtered.map((p) => {
                const status = getStatus(p);
                return (
                  <TableRow key={p.id}>
                    <TableCell className="font-medium">{p.name}</TableCell>
                    <TableCell>{p.diagnosis ?? "—"}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{p.urgency}</Badge>
                    </TableCell>
                    <TableCell>{p.arrival_time}</TableCell>
                    <TableCell>{p.duration} min</TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={
                          status.label === "Diagnosed"
                            ? "border-green-500 text-green-500"
                            : status.label === "In Treatment"
                            ? "border-yellow-500 text-yellow-500"
                            : "text-muted-foreground"
                        }
                      >
                        {status.label}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Progress value={status.pct} />
                    </TableCell>
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center">
                  No patients found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}