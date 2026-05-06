import sys
import re

with open('s:/CECP/landing/templates/landing/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = r'<!-- =============================================================\n\s*TAB 3: INITIATIVES — Full Initiative Cards'
end_marker = r'</section>'

start_match = re.search(start_marker, content)
if not start_match:
    print('Start not found')
    sys.exit(1)

# Find next section to be safe
end_pos = content.find('<!-- =============================================================\n             TAB 4: PROJECTS', start_match.start())
if end_pos == -1:
    print('End not found')
    sys.exit(1)

replacement = r'''<!-- =============================================================
             TAB 3: EVENTS — Full Event Cards
             ============================================================= -->
        <section id="tab-events" class="tab-content h-full overflow-y-auto">
            <div class="relative min-h-[calc(100vh-5rem)] pb-20">
                <div class="ambient-orb orb-indigo" style="width: 500px; height: 500px; bottom: -100px; right: -150px;"></div>
                
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
                    
                    <!-- Header Section with Calendar Icon -->
                    <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-12 gap-8">
                        <div class="max-w-2xl animate-on-scroll">
                            <p class="section-label mb-2 uppercase tracking-widest text-cyan-400 font-bold text-xs">// EVENTS</p>
                            <h2 class="text-5xl md:text-6xl font-black text-white mb-4 tracking-tight leading-tight">
                                Explore <span class="text-cyan-400">Tech</span> Events
                            </h2>
                            <p class="text-slate-400 text-lg md:text-xl leading-relaxed font-light mb-6">
                                Discover hackathons, workshops, competitions and more.<br>
                                Stay ahead. Build. Innovate. Lead.
                            </p>
                            
                            <!-- Stats Bar -->
                            <div class="flex flex-wrap items-center gap-4 md:gap-6 bg-slate-900/50 backdrop-blur-md border border-slate-700/50 rounded-2xl p-4 mt-8">
                                <!-- Stat 1 -->
                                <div class="flex items-center gap-3 pr-4 md:pr-6 border-r border-slate-700/50 last:border-0">
                                    <div class="w-10 h-10 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                    </div>
                                    <div>
                                        <div class="text-white font-bold text-lg leading-tight">25+</div>
                                        <div class="text-[10px] uppercase tracking-wider text-slate-400 font-mono">Events Hosted</div>
                                    </div>
                                </div>
                                <!-- Stat 2 -->
                                <div class="flex items-center gap-3 pr-4 md:pr-6 border-r border-slate-700/50 last:border-0">
                                    <div class="w-10 h-10 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
                                    </div>
                                    <div>
                                        <div class="text-white font-bold text-lg leading-tight">2000+</div>
                                        <div class="text-[10px] uppercase tracking-wider text-slate-400 font-mono">Participants</div>
                                    </div>
                                </div>
                                <!-- Stat 3 -->
                                <div class="flex items-center gap-3 pr-4 md:pr-6 border-r border-slate-700/50 last:border-0">
                                    <div class="w-10 h-10 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                                    </div>
                                    <div>
                                        <div class="text-white font-bold text-lg leading-tight">50+</div>
                                        <div class="text-[10px] uppercase tracking-wider text-slate-400 font-mono">Winners Crowned</div>
                                    </div>
                                </div>
                                <!-- Stat 4 -->
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-xl bg-orange-500/20 text-orange-400 flex items-center justify-center">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                                    </div>
                                    <div>
                                        <div class="text-white font-bold text-lg leading-tight">10+</div>
                                        <div class="text-[10px] uppercase tracking-wider text-slate-400 font-mono">Collaborations</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 3D Calendar Illustration -->
                        <div class="hidden lg:block relative animate-on-scroll flex-shrink-0">
                            <div class="absolute inset-0 bg-blue-500/20 blur-[100px] rounded-full"></div>
                            <div class="relative w-64 h-64 lg:w-80 lg:h-80 flex items-center justify-center">
                                <div class="w-48 h-48 lg:w-56 lg:h-56 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-3xl shadow-[0_20px_60px_rgba(59,130,246,0.6)] border border-blue-400/40 flex flex-col overflow-hidden transform rotate-[-5deg] hover:rotate-0 transition-transform duration-500">
                                    <div class="h-16 bg-blue-400/20 border-b border-blue-400/30 flex items-center justify-center relative shadow-inner">
                                        <!-- Ring binders -->
                                        <div class="absolute -top-4 left-8 w-6 h-10 bg-gradient-to-b from-slate-200 to-slate-400 rounded-full shadow-lg border border-slate-300/50"></div>
                                        <div class="absolute -top-4 right-8 w-6 h-10 bg-gradient-to-b from-slate-200 to-slate-400 rounded-full shadow-lg border border-slate-300/50"></div>
                                    </div>
                                    <div class="flex-1 p-6 grid grid-cols-4 gap-3 relative">
                                        <div class="bg-white/10 rounded-md border border-white/20"></div>
                                        <div class="bg-white/10 rounded-md border border-white/20"></div>
                                        <div class="bg-white/10 rounded-md border border-white/20"></div>
                                        <div class="bg-white/10 rounded-md border border-white/20"></div>
                                        <div class="bg-white/10 rounded-md border border-white/20"></div>
                                        <div class="bg-white/10 rounded-md border border-white/20"></div>
                                        <div class="bg-white/10 rounded-md border border-white/20"></div>
                                        <div class="bg-white/10 rounded-md border border-white/20"></div>
                                        <div class="bg-white/10 rounded-md border border-white/20"></div>
                                        <div class="bg-white/10 rounded-md border border-white/20"></div>
                                        <div class="col-span-2 row-span-2 relative">
                                            <div class="absolute inset-0 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-xl shadow-[0_0_30px_rgba(34,211,238,0.6)] flex items-center justify-center border border-white/30">
                                                <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
                                            </div>
                                        </div>
                                        <div class="bg-white/10 rounded-md border border-white/20"></div>
                                        <div class="bg-white/10 rounded-md border border-white/20"></div>
                                    </div>
                                    <!-- A glowing base line -->
                                    <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-80"></div>
                                </div>
                                <!-- Base reflection/shadow -->
                                <div class="absolute -bottom-6 left-1/2 -translate-x-1/2 w-64 h-8 bg-blue-500/40 blur-2xl rounded-full"></div>
                            </div>
                        </div>
                    </div>

                    <!-- Filters and Search -->
                    <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-10 animate-on-scroll">
                        <div class="flex flex-wrap gap-2 w-full lg:w-auto">
                            <button class="px-4 py-2 rounded-lg bg-slate-800 text-white border border-slate-600 text-sm font-medium flex items-center gap-2 hover:bg-slate-700 transition-colors">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
                                All Events
                            </button>
                            <button class="px-4 py-2 rounded-lg bg-transparent text-slate-400 border border-transparent hover:bg-slate-800/50 hover:text-slate-300 text-sm font-medium transition-colors flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
                                Hackathons
                            </button>
                            <button class="px-4 py-2 rounded-lg bg-transparent text-slate-400 border border-transparent hover:bg-slate-800/50 hover:text-slate-300 text-sm font-medium transition-colors flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                                Workshops
                            </button>
                            <button class="px-4 py-2 rounded-lg bg-transparent text-slate-400 border border-transparent hover:bg-slate-800/50 hover:text-slate-300 text-sm font-medium transition-colors flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                Competitions
                            </button>
                            <button class="px-4 py-2 rounded-lg bg-transparent text-slate-400 border border-transparent hover:bg-slate-800/50 hover:text-slate-300 text-sm font-medium transition-colors flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
                                Talks
                            </button>
                            <button class="px-4 py-2 rounded-lg bg-transparent text-slate-400 border border-transparent hover:bg-slate-800/50 hover:text-slate-300 text-sm font-medium transition-colors flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                Ongoing
                            </button>
                            <button class="px-4 py-2 rounded-lg bg-transparent text-slate-400 border border-transparent hover:bg-slate-800/50 hover:text-slate-300 text-sm font-medium transition-colors">
                                Past Events
                            </button>
                        </div>
                        <div class="relative w-full lg:w-72 flex-shrink-0">
                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                            </div>
                            <input type="text" class="bg-slate-900/80 border border-slate-700/80 text-white text-sm rounded-lg focus:ring-cyan-500 focus:border-cyan-500 block w-full pl-10 p-2.5 placeholder-slate-500 shadow-inner" placeholder="Search events...">
                        </div>
                    </div>

                    <!-- Events Grid -->
                    <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6 animate-on-scroll delay-1">
                        
                        <!-- Card 1: TECHNOMAX 5.0 -->
                        <div class="bg-slate-900/80 border border-slate-700/60 rounded-2xl overflow-hidden hover:border-purple-500/50 hover:shadow-[0_0_30px_rgba(168,85,247,0.15)] transition-all duration-300 flex flex-col group relative">
                            <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500 to-indigo-500 z-20"></div>
                            <div class="h-40 bg-[url('https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center relative overflow-hidden">
                                <div class="absolute inset-0 bg-indigo-900/40 group-hover:bg-indigo-900/20 transition-colors"></div>
                                <div class="absolute top-3 left-3 bg-purple-600 text-white text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded shadow-lg z-10">Featured</div>
                            </div>
                            <div class="p-5 flex-1 flex flex-col relative z-10 -mt-6">
                                <div class="bg-slate-900 border border-slate-700 w-max px-3 py-1 rounded text-xs font-mono text-cyan-400 mb-3 shadow-lg">Hackathon</div>
                                <h3 class="text-xl font-bold text-white mb-2">TECHNOMAX 5.0</h3>
                                <p class="text-sm text-slate-400 mb-4 line-clamp-2 leading-relaxed flex-1">National level electronics hackathon. Innovate. Integrate. Inspire.</p>
                                
                                <div class="space-y-2 mb-6">
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                        24-26 May 2025
                                    </div>
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.243-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                                        CECP, Bhopal
                                    </div>
                                </div>
                                <div class="flex items-center justify-between mt-auto">
                                    <a href="#" class="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium py-2 px-4 rounded transition-colors flex items-center gap-2 shadow-[0_0_15px_rgba(79,70,229,0.3)]">
                                        Register Now <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                                    </a>
                                    <button class="text-slate-400 hover:text-white transition-colors">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Card 2: PCB DESIGN WORKSHOP -->
                        <div class="bg-slate-900/80 border border-slate-700/60 rounded-2xl overflow-hidden hover:border-green-500/50 hover:shadow-[0_0_30px_rgba(34,197,94,0.15)] transition-all duration-300 flex flex-col group relative">
                            <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-green-500 to-emerald-500 z-20"></div>
                            <div class="h-40 bg-[url('https://images.unsplash.com/photo-1592503254549-ceb5b3a3250b?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center relative overflow-hidden">
                                <div class="absolute inset-0 bg-green-900/40 group-hover:bg-green-900/20 transition-colors"></div>
                                <div class="absolute top-3 left-3 bg-green-600 text-white text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded shadow-lg z-10 flex items-center gap-1">
                                    <span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span> Live Now
                                </div>
                            </div>
                            <div class="p-5 flex-1 flex flex-col relative z-10 -mt-6">
                                <div class="bg-slate-900 border border-slate-700 w-max px-3 py-1 rounded text-xs font-mono text-blue-400 mb-3 shadow-lg">Workshop</div>
                                <h3 class="text-xl font-bold text-white mb-2">PCB DESIGN WORKSHOP</h3>
                                <p class="text-sm text-slate-400 mb-4 line-clamp-2 leading-relaxed flex-1">Learn PCB designing from basics to advanced with hands-on practice.</p>
                                
                                <div class="space-y-2 mb-6">
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                        18 May 2025
                                    </div>
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
                                        Electronics Lab
                                    </div>
                                </div>
                                <div class="flex items-center justify-between mt-auto">
                                    <a href="#" class="bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium py-2 px-4 rounded transition-colors flex items-center gap-2 shadow-[0_0_15px_rgba(37,99,235,0.3)]">
                                        View Details <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                                    </a>
                                    <button class="text-slate-400 hover:text-white transition-colors">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Card 3: CIRCUIT DEBUGGING -->
                        <div class="bg-slate-900/80 border border-slate-700/60 rounded-2xl overflow-hidden hover:border-cyan-500/50 hover:shadow-[0_0_30px_rgba(6,182,212,0.15)] transition-all duration-300 flex flex-col group relative">
                            <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-blue-500 z-20"></div>
                            <div class="h-40 bg-[url('https://images.unsplash.com/photo-1620803553258-a53c1af7ebf1?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center relative overflow-hidden">
                                <div class="absolute inset-0 bg-cyan-900/40 group-hover:bg-cyan-900/20 transition-colors"></div>
                                <div class="absolute top-3 left-3 bg-cyan-600 text-white text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded shadow-lg z-10">Upcoming</div>
                            </div>
                            <div class="p-5 flex-1 flex flex-col relative z-10 -mt-6">
                                <div class="bg-slate-900 border border-slate-700 w-max px-3 py-1 rounded text-xs font-mono text-purple-400 mb-3 shadow-lg">Competition</div>
                                <h3 class="text-xl font-bold text-white mb-2">CIRCUIT DEBUGGING</h3>
                                <p class="text-sm text-slate-400 mb-4 line-clamp-2 leading-relaxed flex-1">Test your troubleshooting skills in real-world circuits.</p>
                                
                                <div class="space-y-2 mb-6">
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                        25 May 2025
                                    </div>
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.243-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                                        CECP, Bhopal
                                    </div>
                                </div>
                                <div class="flex items-center justify-between mt-auto">
                                    <a href="#" class="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium py-2 px-4 rounded transition-colors flex items-center gap-2 shadow-[0_0_15px_rgba(79,70,229,0.3)]">
                                        Register Now <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                                    </a>
                                    <button class="text-slate-400 hover:text-white transition-colors">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Card 4: SOLDERING BOOTCAMP -->
                        <div class="bg-slate-900/80 border border-slate-700/60 rounded-2xl overflow-hidden hover:border-blue-500/50 hover:shadow-[0_0_30px_rgba(59,130,246,0.15)] transition-all duration-300 flex flex-col group relative">
                            <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-indigo-500 z-20"></div>
                            <div class="h-40 bg-[url('https://images.unsplash.com/photo-1591523456382-78d1033068e2?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center relative overflow-hidden">
                                <div class="absolute inset-0 bg-blue-900/40 group-hover:bg-blue-900/20 transition-colors"></div>
                                <div class="absolute top-3 left-3 bg-blue-600 text-white text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded shadow-lg z-10">Upcoming</div>
                            </div>
                            <div class="p-5 flex-1 flex flex-col relative z-10 -mt-6">
                                <div class="bg-slate-900 border border-slate-700 w-max px-3 py-1 rounded text-xs font-mono text-cyan-400 mb-3 shadow-lg">Workshop</div>
                                <h3 class="text-xl font-bold text-white mb-2">SOLDERING BOOTCAMP</h3>
                                <p class="text-sm text-slate-400 mb-4 line-clamp-2 leading-relaxed flex-1">Master the art of soldering with expert guidance.</p>
                                
                                <div class="space-y-2 mb-6">
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                        1 June 2025
                                    </div>
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
                                        Electronics Lab
                                    </div>
                                </div>
                                <div class="flex items-center justify-between mt-auto">
                                    <a href="#" class="bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium py-2 px-4 rounded transition-colors flex items-center gap-2 shadow-[0_0_15px_rgba(37,99,235,0.3)]">
                                        View Details <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                                    </a>
                                    <button class="text-slate-400 hover:text-white transition-colors">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Card 5: ROBO RUMBLE 2.0 -->
                        <div class="bg-slate-900/80 border border-slate-700/60 rounded-2xl overflow-hidden hover:border-slate-500/50 hover:shadow-[0_0_30px_rgba(148,163,184,0.15)] transition-all duration-300 flex flex-col group relative opacity-80">
                            <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-slate-500 to-slate-400 z-20"></div>
                            <div class="h-40 bg-[url('https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center relative overflow-hidden filter grayscale-[50%]">
                                <div class="absolute inset-0 bg-slate-900/60 group-hover:bg-slate-900/40 transition-colors"></div>
                                <div class="absolute top-3 left-3 bg-slate-600 text-white text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded shadow-lg z-10">Completed</div>
                            </div>
                            <div class="p-5 flex-1 flex flex-col relative z-10 -mt-6">
                                <div class="bg-slate-900 border border-slate-700 w-max px-3 py-1 rounded text-xs font-mono text-purple-400 mb-3 shadow-lg">Competition</div>
                                <h3 class="text-xl font-bold text-white mb-2">ROBO RUMBLE 2.0</h3>
                                <p class="text-sm text-slate-400 mb-4 line-clamp-2 leading-relaxed flex-1">An exciting robotics competition for tech innovators.</p>
                                
                                <div class="space-y-2 mb-6">
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                        10 May 2025
                                    </div>
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.243-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                                        CECP, Bhopal
                                    </div>
                                </div>
                                <div class="flex items-center justify-between mt-auto">
                                    <a href="#" class="bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium py-2 px-4 rounded transition-colors flex items-center gap-2">
                                        View Highlights <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                                    </a>
                                    <button class="text-slate-400 hover:text-white transition-colors">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Card 6: INDUSTRY TALK -->
                        <div class="bg-slate-900/80 border border-slate-700/60 rounded-2xl overflow-hidden hover:border-cyan-500/50 hover:shadow-[0_0_30px_rgba(6,182,212,0.15)] transition-all duration-300 flex flex-col group relative">
                            <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-blue-500 z-20"></div>
                            <div class="h-40 bg-[url('https://images.unsplash.com/photo-1540317580384-e5d43867caa6?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center relative overflow-hidden">
                                <div class="absolute inset-0 bg-cyan-900/40 group-hover:bg-cyan-900/20 transition-colors"></div>
                                <div class="absolute top-3 left-3 bg-cyan-600 text-white text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded shadow-lg z-10">Upcoming</div>
                            </div>
                            <div class="p-5 flex-1 flex flex-col relative z-10 -mt-6">
                                <div class="bg-slate-900 border border-slate-700 w-max px-3 py-1 rounded text-xs font-mono text-blue-400 mb-3 shadow-lg">Talk</div>
                                <h3 class="text-xl font-bold text-white mb-2">INDUSTRY TALK</h3>
                                <p class="text-sm text-slate-400 mb-4 line-clamp-2 leading-relaxed flex-1">Insights from industry experts on emerging technologies.</p>
                                
                                <div class="space-y-2 mb-6">
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                        5 June 2025
                                    </div>
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                                        Online (Zoom)
                                    </div>
                                </div>
                                <div class="flex items-center justify-between mt-auto">
                                    <a href="#" class="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium py-2 px-4 rounded transition-colors flex items-center gap-2 shadow-[0_0_15px_rgba(79,70,229,0.3)]">
                                        Register Now <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                                    </a>
                                    <button class="text-slate-400 hover:text-white transition-colors">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
                                    </button>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>

                <footer class="border-t border-slate-800/50 py-8 mt-12">
                    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                        <p class="text-xs text-slate-600">&copy; {% now "Y" %} CECP — Roorkee Institute of Technology
                        </p>
                    </div>
                </footer>
            </div>
        </section>'''

new_content = content[:start_match.start()] + replacement + content[end_pos:]

with open('s:/CECP/landing/templates/landing/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Replacement successful')
