"use client";
import {
    Sidebar,
    SidebarGroup,
    SidebarContent,
    SidebarFooter,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuItem,
    SidebarMenuButton,
    SidebarMenuSub,
    SidebarMenuSubItem,
    SidebarMenuSubButton,
} from "@/components/ui/sidebar"

import {
    ChevronDown,
    LayoutDashboard,
} from "lucide-react"

import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/collapsible"
import { useRouter } from "next/navigation";
import { AddPatient } from "./patient/Add";


export function AppSidebar() {

    const router = useRouter();

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
                                render={
                                    <SidebarMenuButton />
                                }
                            >
                                <span>Patients</span>
                                <ChevronDown className="ml-auto" />
                            </CollapsibleTrigger>

                            <CollapsibleContent>
                                <SidebarMenuSub>
                                    <SidebarMenuSubItem>
                                        {/* <SidebarMenuSubButton onClick={()=>router.push('/patients/add')}>
                                            Add
                                        </SidebarMenuSubButton> */}

                                        <AddPatient />
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
                                render={
                                    <SidebarMenuButton />
                                }
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
    )
}