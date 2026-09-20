"use client";

import { useState } from "react";

import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuItem,
    SidebarMenuButton,
    SidebarMenuSub,
    SidebarMenuSubItem,
    SidebarMenuSubButton,
} from "@/components/ui/sidebar";

import {
    ChevronDown,
    LayoutDashboard,
} from "lucide-react";

import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/collapsible";

import { AddPatient } from "@/components/patient/Add";


export function AppSidebar() {
    const [addPatientOpen, setAddPatientOpen] = useState(false);

    return (
        <Sidebar>

            <SidebarHeader className="h-14" />

            <SidebarContent className="px-3">
                <SidebarMenu>

                    {/* Dashboard */}
                    <SidebarMenuItem>
                        <SidebarMenuButton>
                            <LayoutDashboard />
                            <span>Dashboard</span>
                        </SidebarMenuButton>
                    </SidebarMenuItem>


                    {/* Patients */}
                    <SidebarMenuItem>
                        <Collapsible defaultOpen>

                            <CollapsibleTrigger
                                render={<SidebarMenuButton />}
                            >
                                <span>Patients</span>
                                <ChevronDown className="ml-auto" />
                            </CollapsibleTrigger>

                            <CollapsibleContent>
                                <SidebarMenuSub>

                                    <SidebarMenuSubItem>
                                        <SidebarMenuSubButton
                                            onClick={() => setAddPatientOpen(true)}
                                        >
                                            Add
                                            {/* Dialog */}
                                            <AddPatient
                                                open={addPatientOpen}
                                                onOpenChange={setAddPatientOpen}
                                            />
                                        </SidebarMenuSubButton>
                                    </SidebarMenuSubItem>

                                    <SidebarMenuSubItem>
                                        <SidebarMenuSubButton>
                                            Manage
                                        </SidebarMenuSubButton>
                                    </SidebarMenuSubItem>

                                </SidebarMenuSub>
                            </CollapsibleContent>

                        </Collapsible>
                    </SidebarMenuItem>


                    {/* Doctors */}
                    <SidebarMenuItem>
                        <Collapsible defaultOpen>

                            <CollapsibleTrigger
                                render={<SidebarMenuButton />}
                            >
                                <span>Doctors</span>
                                <ChevronDown className="ml-auto" />
                            </CollapsibleTrigger>

                            <CollapsibleContent>
                                <SidebarMenuSub>

                                    <SidebarMenuSubItem>
                                        <SidebarMenuSubButton>
                                            Add
                                        </SidebarMenuSubButton>
                                    </SidebarMenuSubItem>

                                    <SidebarMenuSubItem>
                                        <SidebarMenuSubButton>
                                            Manage
                                        </SidebarMenuSubButton>
                                    </SidebarMenuSubItem>

                                </SidebarMenuSub>
                            </CollapsibleContent>

                        </Collapsible>
                    </SidebarMenuItem>

                </SidebarMenu>
            </SidebarContent>

            <SidebarFooter />

        </Sidebar>
    );
}