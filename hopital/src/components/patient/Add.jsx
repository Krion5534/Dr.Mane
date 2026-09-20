"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { Button } from "@/components/ui/button";

import {
  Field,
  FieldContent,
  FieldDescription,
  FieldLabel,
  FieldLegend,
  FieldSet,
} from "@/components/ui/field";

import { Input } from "@/components/ui/input";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { useState } from "react";

export function AddPatient({ open, onOpenChange }) {

  const [isChild, setChild] = useState(true);
  const [highUrgency, setHighUrgency] = useState(false);
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [urgency, setUrgency] = useState("");
  const [diagnosis, setDiagnosis] = useState("");


  const backend_url = process.env.NEXT_PUBLIC_BACKEND_URL;


  const handleSubmit = async (e) => {
    e.preventDefault();

    const response = await fetch(
      backend_url+"/patients/admit",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          age: Number(age),
          urgency: Number(urgency),
          diagnosis,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      console.error(data);
      return;
    }

    console.log("Admitted:", data.patient);

    onOpenChange(false);

    // optional reset
    setName("");
    setAge("");
    setUrgency("");
    setDiagnosis("");
  };


  const handleAge = (e) => {
    let age = e.target.value
    console.log(age)
    if (age > 16) setChild(false);
    else setChild(true);
  }

  const handleUrgency = (value) => {
    const highUrgency = [
      "Heart Attack",
      "Cardiac Arrest",
      "Stroke",
      "Brain Hemorrhage",
    ];
    setHighUrgency(highUrgency.includes(value));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[550px]">
        <DialogHeader>
          <DialogTitle>Admit a Patient</DialogTitle>

          <DialogDescription>
            Enter the patient's information below.
          </DialogDescription>
        </DialogHeader>

        <div className="mx-4 max-h-[60vh] overflow-y-auto px-4">
          <form className="space-y-6"
            onSubmit={handleSubmit}>

            {/* Patient Name */}
            <Field>
              <FieldLabel htmlFor="patient-name">
                Patient Name
              </FieldLabel>

              <FieldContent>
                <Input
                  id="patient-name"
                  name="name"
                  type="text"
                  placeholder="e.g. Krion"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />

                <FieldDescription>
                  Patient's name.
                </FieldDescription>
              </FieldContent>
            </Field>


            {/* Age */}
            <Field>
              <FieldLabel htmlFor="patient-age">
                Age
              </FieldLabel>

              <FieldContent>
                <Input
                  id="patient-age"
                  name="age"
                  type="number"
                  min="0"
                  max="120"
                  value={age}
                  onChange={(e) => {
                    setAge(e.target.value);
                    handleAge(e);
                  }}
                  placeholder="e.g. 67"
                />
              </FieldContent>
            </Field>



            {/* Urgency */}
            <Field>
              <FieldLabel htmlFor="patient-urgency">
                Urgency
              </FieldLabel>

              <FieldContent>
                <Select name="urgency"
                  value={urgency}
                  onValueChange={setUrgency}>
                  <SelectTrigger id="patient-urgency">
                    <SelectValue placeholder="Select urgency" />
                  </SelectTrigger>

                  <SelectContent>
                    <SelectItem value="1">
                      1 — Critical
                    </SelectItem>
                    {!highUrgency && (<div>
                      <SelectItem value="2">
                        2 — High
                      </SelectItem>

                      <SelectItem value="3">
                        3 — Moderate
                      </SelectItem>

                      <SelectItem value="4">
                        4 — Low
                      </SelectItem>
                    </div>)}
                  </SelectContent>
                </Select>

                <FieldDescription>
                  1 is the most urgent and 4 is the least urgent.
                </FieldDescription>
              </FieldContent>
            </Field>



            {/* Diagnosis */}
            <Field>
              <FieldLabel htmlFor="patient-diagnosis">
                Diagnosis
              </FieldLabel>

              <FieldContent>
                <Select name="diagnosis"
                  value={diagnosis}
                  onValueChange={(value) => {
                    setDiagnosis(value);
                    handleUrgency(value);
                  }}>
                  <SelectTrigger id="patient-diagnosis">
                    <SelectValue placeholder="Select diagnosis" />
                  </SelectTrigger>

                  <SelectContent>

                    <SelectItem value="Heart Attack">
                      Heart Attack
                    </SelectItem>

                    <SelectItem value="Cardiac Arrest">
                      Cardiac Arrest
                    </SelectItem>

                    <SelectItem value="Stroke">
                      Stroke
                    </SelectItem>

                    <SelectItem value="Brain Hemorrhage">
                      Brain Hemorrhage
                    </SelectItem>

                    {
                      isChild && <div>
                        <SelectItem value="Pediatric Fever">
                          Pediatric Fever
                        </SelectItem>

                        <SelectItem value="Childhood Asthma">
                          Childhood Asthma
                        </SelectItem>
                      </div>
                    }
                  </SelectContent>
                </Select>

                <FieldDescription>
                  Select patient's diagnosis
                </FieldDescription>
              </FieldContent>
            </Field>

          </form>
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Cancel
          </Button>

          <Button type="submit">
            Admit Patient
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}