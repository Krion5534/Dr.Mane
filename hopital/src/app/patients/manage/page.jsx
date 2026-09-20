"use client";

import { useEffect, useState } from "react";

import {
  Activity,
  AlertTriangle,
  Clock,
  Eye,
  MoreHorizontal,
  Pencil,
  RefreshCw,
  Trash2,
  UserRound,
  Users,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { Badge } from "@/components/ui/badge";

import { Button } from "@/components/ui/button";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

import { Separator } from "@/components/ui/separator";

import { Input } from "@/components/ui/input";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";


const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL;


export default function PatientManager() {

  const [patients, setPatients] = useState([]);

  const [selectedPatient, setSelectedPatient] = useState(null);
  const [viewOpen, setViewOpen] = useState(false);

  const [editPatient, setEditPatient] = useState(null);
  const [editOpen, setEditOpen] = useState(false);

  const [deletePatient, setDeletePatient] = useState(null);
  const [deleteOpen, setDeleteOpen] = useState(false);

  const [connected, setConnected] = useState(false);


  // ------------------------------------------------------------
  // WebSocket
  // ------------------------------------------------------------

  useEffect(() => {

    const wsUrl =
      API_URL.replace("http://", "ws://")
        .replace("https://", "wss://") +
      "/api/patients/view/all";

    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      setConnected(true);
    };

    socket.onmessage = (event) => {

      const data = JSON.parse(event.data);

      if (data.type === "patients_update") {
        setPatients(data.patients);
      }

    };

    socket.onclose = () => {
      setConnected(false);
    };

    socket.onerror = () => {
      setConnected(false);
    };

    return () => {
      socket.close();
    };

  }, []);


  // ------------------------------------------------------------
  // View
  // ------------------------------------------------------------

  function handleView(patient) {
    setSelectedPatient(patient);
    setViewOpen(true);
  }


  // ------------------------------------------------------------
  // Edit
  // ------------------------------------------------------------

  function handleEdit(patient) {
    setEditPatient({
      ...patient,
    });

    setEditOpen(true);
  }


  async function saveEdit() {

    if (!editPatient) {
      return;
    }

    const response = await fetch(
      `${API_URL}/api/patients/${editPatient.id}`,
      {
        method: "PATCH",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          name: editPatient.name,
          age: Number(editPatient.age),
          urgency: Number(editPatient.urgency),
          diagnosis: editPatient.diagnosis,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      console.error(data);
      return;
    }

    setEditOpen(false);
  }


  // ------------------------------------------------------------
  // Delete
  // ------------------------------------------------------------

  function handleDelete(patient) {
    setDeletePatient(patient);
    setDeleteOpen(true);
  }


  async function confirmDelete() {

    if (!deletePatient) {
      return;
    }

    const response = await fetch(
      `${API_URL}/patients/${deletePatient.id}`,
      {
        method: "DELETE",
      }
    );

    const data = await response.json();

    if (!response.ok) {
      console.error(data);
      return;
    }

    setDeleteOpen(false);
    setDeletePatient(null);
  }


  // ------------------------------------------------------------
  // Stats
  // ------------------------------------------------------------

  const criticalPatients = patients.filter(
    (patient) => patient.urgency === 1
  ).length;

  const waitingPatients = patients.filter(
    (patient) => patient.start_time === null
  ).length;

  const treatmentPatients = patients.filter(
    (patient) => patient.start_time !== null && patient.end_time === null
  ).length;


  return (
    <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">

      {/* Header */}

      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">

        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Manage Patients
          </h1>

          <p className="text-muted-foreground">
            View and manage patients currently registered in the hospital.
          </p>
        </div>

        <div className="flex items-center gap-2">

          <Badge
            variant={connected ? "default" : "destructive"}
            className="gap-1.5"
          >
            <span
              className={`size-2 rounded-full ${
                connected
                  ? "bg-background"
                  : "bg-background"
              }`}
            />

            {connected ? "Live" : "Disconnected"}
          </Badge>

        </div>

      </div>


      {/* Stats */}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardDescription>Total Patients</CardDescription>
            <Users className="size-4 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-2xl font-semibold">
              {patients.length}
            </div>
          </CardContent>
        </Card>


        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardDescription>Waiting</CardDescription>
            <Clock className="size-4 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-2xl font-semibold">
              {waitingPatients}
            </div>
          </CardContent>
        </Card>


        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardDescription>In Treatment</CardDescription>
            <Activity className="size-4 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-2xl font-semibold">
              {treatmentPatients}
            </div>
          </CardContent>
        </Card>


        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardDescription>Critical</CardDescription>
            <AlertTriangle className="size-4 text-muted-foreground" />
          </CardHeader>

          <CardContent>
            <div className="text-2xl font-semibold">
              {criticalPatients}
            </div>
          </CardContent>
        </Card>

      </div>


      {/* Patient table */}

      <Card>

        <CardHeader>

          <div className="flex items-center justify-between">

            <div>
              <CardTitle>Patients</CardTitle>

              <CardDescription>
                Patient information is updated in real time.
              </CardDescription>
            </div>

            <RefreshCw
              className={`size-4 text-muted-foreground ${
                connected ? "animate-pulse" : ""
              }`}
            />

          </div>

        </CardHeader>


        <CardContent>

          <div className="rounded-md border">

            <Table>

              <TableHeader>

                <TableRow>

                  <TableHead>ID</TableHead>

                  <TableHead>Patient</TableHead>

                  <TableHead>Age</TableHead>

                  <TableHead>Urgency</TableHead>

                  <TableHead>Diagnosis</TableHead>

                  <TableHead>Specialty</TableHead>

                  <TableHead>Status</TableHead>

                  <TableHead className="text-right">
                    Actions
                  </TableHead>

                </TableRow>

              </TableHeader>


              <TableBody>

                {patients.length === 0 ? (

                  <TableRow>

                    <TableCell
                      colSpan={8}
                      className="h-32 text-center"
                    >
                      <div className="flex flex-col items-center gap-2 text-muted-foreground">
                        <UserRound className="size-8" />
                        <span>No patients found.</span>
                      </div>
                    </TableCell>

                  </TableRow>

                ) : (

                  patients.map((patient) => (

                    <TableRow key={patient.id}>

                      <TableCell className="font-mono">
                        #{patient.id}
                      </TableCell>


                      <TableCell className="font-medium">
                        {patient.name}
                      </TableCell>


                      <TableCell>
                        {patient.age}
                      </TableCell>


                      <TableCell>
                        <UrgencyBadge
                          urgency={patient.urgency}
                        />
                      </TableCell>


                      <TableCell>
                        {patient.diagnosis || "—"}
                      </TableCell>


                      <TableCell>
                        {patient.required_specialty}
                      </TableCell>


                      <TableCell>
                        <PatientStatus patient={patient} />
                      </TableCell>


                      <TableCell className="text-right">

                        <DropdownMenu>

                          <DropdownMenuTrigger
                            render={
                              <Button
                                variant="ghost"
                                size="icon"
                              />
                            }
                          >
                            <MoreHorizontal />
                            <span className="sr-only">
                              Patient actions
                            </span>
                          </DropdownMenuTrigger>


                          <DropdownMenuContent align="end">

                            <DropdownMenuItem
                              onClick={() => handleView(patient)}
                            >
                              <Eye />
                              View patient
                            </DropdownMenuItem>


                            <DropdownMenuItem
                              onClick={() => handleEdit(patient)}
                            >
                              <Pencil />
                              Edit patient
                            </DropdownMenuItem>


                            <DropdownMenuSeparator />


                            <DropdownMenuItem
                              variant="destructive"
                              onClick={() => handleDelete(patient)}
                            >
                              <Trash2 />
                              Delete patient
                            </DropdownMenuItem>

                          </DropdownMenuContent>

                        </DropdownMenu>

                      </TableCell>

                    </TableRow>

                  ))

                )}

              </TableBody>

            </Table>

          </div>

        </CardContent>

      </Card>


      {/* ------------------------------------------------------ */}
      {/* View Patient Dialog */}
      {/* ------------------------------------------------------ */}

      <PatientDetailsDialog
        patient={selectedPatient}
        open={viewOpen}
        onOpenChange={setViewOpen}
      />


      {/* ------------------------------------------------------ */}
      {/* Edit Patient Dialog */}
      {/* ------------------------------------------------------ */}

      <Dialog
        open={editOpen}
        onOpenChange={setEditOpen}
      >

        <DialogContent className="sm:max-w-[500px]">

          <DialogHeader>

            <DialogTitle>
              Edit Patient
            </DialogTitle>

            <DialogDescription>
              Update the patient's information.
            </DialogDescription>

          </DialogHeader>


          {editPatient && (

            <div className="space-y-4">

              <div className="space-y-2">

                <label className="text-sm font-medium">
                  Name
                </label>

                <Input
                  value={editPatient.name}
                  onChange={(e) =>
                    setEditPatient({
                      ...editPatient,
                      name: e.target.value,
                    })
                  }
                />

              </div>


              <div className="space-y-2">

                <label className="text-sm font-medium">
                  Age
                </label>

                <Input
                  type="number"
                  min="0"
                  max="120"
                  value={editPatient.age}
                  onChange={(e) =>
                    setEditPatient({
                      ...editPatient,
                      age: e.target.value,
                    })
                  }
                />

              </div>


              <div className="space-y-2">

                <label className="text-sm font-medium">
                  Urgency
                </label>

                <Select
                  value={String(editPatient.urgency)}
                  onValueChange={(value) =>
                    setEditPatient({
                      ...editPatient,
                      urgency: Number(value),
                    })
                  }
                >

                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>

                  <SelectContent>

                    <SelectItem value="1">
                      1 — Critical
                    </SelectItem>

                    <SelectItem value="2">
                      2 — High
                    </SelectItem>

                    <SelectItem value="3">
                      3 — Moderate
                    </SelectItem>

                    <SelectItem value="4">
                      4 — Low
                    </SelectItem>

                  </SelectContent>

                </Select>

              </div>


              <div className="space-y-2">

                <label className="text-sm font-medium">
                  Diagnosis
                </label>

                <Input
                  value={editPatient.diagnosis || ""}
                  onChange={(e) =>
                    setEditPatient({
                      ...editPatient,
                      diagnosis: e.target.value,
                    })
                  }
                />

              </div>

            </div>

          )}


          <DialogFooter>

            <Button
              variant="outline"
              onClick={() => setEditOpen(false)}
            >
              Cancel
            </Button>

            <Button onClick={saveEdit}>
              Save changes
            </Button>

          </DialogFooter>

        </DialogContent>

      </Dialog>


      {/* ------------------------------------------------------ */}
      {/* Delete confirmation */}
      {/* ------------------------------------------------------ */}

      <AlertDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
      >

        <AlertDialogContent>

          <AlertDialogHeader>

            <AlertDialogTitle>
              Delete patient?
            </AlertDialogTitle>

            <AlertDialogDescription>
              This will permanently remove{" "}
              <span className="font-medium">
                {deletePatient?.name}
              </span>{" "}
              from the current hospital session.
              This action cannot be undone.
            </AlertDialogDescription>

          </AlertDialogHeader>


          <AlertDialogFooter>

            <AlertDialogCancel>
              Cancel
            </AlertDialogCancel>

            <AlertDialogAction
              variant="destructive"
              onClick={confirmDelete}
            >
              Delete patient
            </AlertDialogAction>

          </AlertDialogFooter>

        </AlertDialogContent>

      </AlertDialog>

    </div>
  );
}


/* ============================================================ */
/* Urgency Badge */
/* ============================================================ */

function UrgencyBadge({ urgency }) {

  const labels = {
    1: "Critical",
    2: "High",
    3: "Moderate",
    4: "Low",
  };

  const variants = {
    1: "destructive",
    2: "secondary",
    3: "outline",
    4: "outline",
  };

  return (
    <Badge variant={variants[urgency] || "outline"}>
      {urgency} — {labels[urgency] || "Unknown"}
    </Badge>
  );
}


/* ============================================================ */
/* Patient Status */
/* ============================================================ */

function PatientStatus({ patient }) {

  if (patient.died) {
    return (
      <Badge variant="destructive">
        Deceased
      </Badge>
    );
  }

  if (patient.end_time) {
    return (
      <Badge variant="outline">
        Completed
      </Badge>
    );
  }

  if (patient.start_time) {
    return (
      <Badge>
        In Treatment
      </Badge>
    );
  }

  return (
    <Badge variant="secondary">
      Waiting
    </Badge>
  );
}


/* ============================================================ */
/* Patient Details Dialog */
/* ============================================================ */

function PatientDetailsDialog({
  patient,
  open,
  onOpenChange,
}) {

  if (!patient) {
    return null;
  }

  return (
    <Dialog
      open={open}
      onOpenChange={onOpenChange}
    >

      <DialogContent className="sm:max-w-[650px]">

        <DialogHeader>

          <DialogTitle className="flex items-center gap-2">
            {patient.name}

            <UrgencyBadge
              urgency={patient.urgency}
            />
          </DialogTitle>

          <DialogDescription>
            Complete patient information
          </DialogDescription>

        </DialogHeader>


        <div className="max-h-[65vh] overflow-y-auto">

          <div className="grid gap-6 px-1">

            {/* Basic information */}

            <section>

              <h3 className="mb-3 text-sm font-medium">
                Patient Information
              </h3>

              <div className="grid grid-cols-2 gap-4">

                <DetailItem
                  label="Patient ID"
                  value={`#${patient.id}`}
                />

                <DetailItem
                  label="Name"
                  value={patient.name}
                />

                <DetailItem
                  label="Age"
                  value={`${patient.age} years`}
                />

                <DetailItem
                  label="Diagnosis"
                  value={patient.diagnosis || "Not diagnosed"}
                />

                <DetailItem
                  label="Required Specialty"
                  value={patient.required_specialty}
                />

                <DetailItem
                  label="Urgency"
                  value={`${patient.urgency}`}
                />

              </div>

            </section>


            <Separator />


            {/* Timeline */}

            <section>

              <h3 className="mb-3 text-sm font-medium">
                Treatment Timeline
              </h3>

              <div className="grid grid-cols-2 gap-4">

                <DetailItem
                  label="Arrival"
                  value={patient.arrival_time || "—"}
                />

                <DetailItem
                  label="Treatment Start"
                  value={patient.start_time || "Waiting"}
                />

                <DetailItem
                  label="Treatment End"
                  value={patient.end_time || "—"}
                />

                <DetailItem
                  label="Waiting Time"
                  value={
                    patient.wait !== null &&
                    patient.wait !== undefined
                      ? `${patient.wait} minutes`
                      : "Still waiting"
                  }
                />

                <DetailItem
                  label="Treatment Duration"
                  value={`${patient.duration} minutes`}
                />

              </div>

            </section>


            <Separator />


            {/* Resources */}

            <section>

              <h3 className="mb-3 text-sm font-medium">
                Resource Requirements
              </h3>

              <div className="grid grid-cols-2 gap-4">

                {Object.entries(patient.needs || {}).map(
                  ([resource, amount]) => (

                    <DetailItem
                      key={resource}
                      label={formatResourceName(resource)}
                      value={amount}
                    />

                  )
                )}

              </div>

            </section>


            <Separator />


            {/* Risk */}

            <section>

              <h3 className="mb-3 text-sm font-medium">
                Risk & Status
              </h3>

              <div className="grid grid-cols-2 gap-4">

                <DetailItem
                  label="Current Death Chance"
                  value={`${patient.death_chance}%`}
                />

                <DetailItem
                  label="Initial Mortality Chance"
                  value={`${patient.mortality_chance}%`}
                />

                <DetailItem
                  label="During Surge"
                  value={patient.during_surge ? "Yes" : "No"}
                />

                <DetailItem
                  label="Downgraded"
                  value={patient.downgraded ? "Yes" : "No"}
                />

                <DetailItem
                  label="Died"
                  value={patient.died ? "Yes" : "No"}
                />

              </div>

            </section>

          </div>

        </div>


        <DialogFooter>

          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Close
          </Button>

        </DialogFooter>

      </DialogContent>

    </Dialog>
  );
}


/* ============================================================ */
/* Detail Item */
/* ============================================================ */

function DetailItem({ label, value }) {

  return (
    <div className="rounded-lg border bg-muted/30 p-3">

      <p className="text-xs text-muted-foreground">
        {label}
      </p>

      <p className="mt-1 text-sm font-medium">
        {value}
      </p>

    </div>
  );
}


/* ============================================================ */
/* Resource formatting */
/* ============================================================ */

function formatResourceName(resource) {

  return resource
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}