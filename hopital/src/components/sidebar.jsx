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


export function AppSidebar() {
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
                            <CollapsibleTrigger className="w-full">
                                <SidebarMenuButton>
                                    <span>Patients</span>
                                    <ChevronDown className="ml-auto" />
                                </SidebarMenuButton>
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


                    {/* Doctors */}
                    <SidebarMenuItem>
                        <Collapsible defaultOpen>
                            <CollapsibleTrigger className="w-full">
                                <SidebarMenuButton>
                                    <span>Doctors</span>
                                    <ChevronDown className="ml-auto" />
                                </SidebarMenuButton>
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