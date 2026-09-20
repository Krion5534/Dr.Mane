"use client";

import { useEffect, useState } from "react";

import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const DIAGNOSIS_OPTIONS = [
  "Heart Attack",
  "Cardiac Arrest",
  "Stroke",
  "Brain Hemorrhage",
  "Fracture",
  "Joint Dislocation",
  "Severe Rash",
  "Skin Infection",
  "Pediatric Fever",
  "Childhood Asthma",
];

const backend_url = process.env.NEXT_PUBLIC_BACKEND_URL;

export default function DiagnosesPage() {
  const [patients, setPatients] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchPatients = async () => {
    const res = await fetch(`${backend_url}/api/patients/all`, { cache: "no-store" });
    const data = await res.json();
    setPatients(data.patients || []);
    setLoading(false);
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const updateDiagnosis = async (patientId, diagnosis) => {
    // optimistic update
    setPatients((prev) =>
      prev.map((p) => (p.id === patientId ? { ...p, diagnosis } : p))
    );

    const res = await fetch(`${backend_url}/api/patients/${patientId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ diagnosis }),
    });

    if (!res.ok) {
      // revert on failure
      fetchPatients();
    }
  };

  const filtered = patients.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-1 flex-col gap-4 p-4 lg:p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Manage Diagnoses</h1>
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
              <TableHead>Age</TableHead>
              <TableHead>Urgency</TableHead>
              <TableHead>Specialty</TableHead>
              <TableHead>Diagnosis</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : filtered.length ? (
              filtered.map((p) => (
                <TableRow key={p.id}>
                  <TableCell className="font-medium">{p.name}</TableCell>
                  <TableCell>{p.age}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{p.urgency}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="text-muted-foreground">
                      {p.required_specialty}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Select
                      value={p.diagnosis || ""}
                      onValueChange={(value) => updateDiagnosis(p.id, value)}
                    >
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Select diagnosis" />
                      </SelectTrigger>
                      <SelectContent>
                        {(p.age < 16
                          ? ["Pediatric Fever", "Childhood Asthma"]
                          : DIAGNOSIS_OPTIONS
                        ).map((d) => (
                          <SelectItem key={d} value={d}>
                            {d}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center">
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