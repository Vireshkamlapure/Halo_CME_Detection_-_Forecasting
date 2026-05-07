import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Radio, Eye, Command, Zap, Database, Shield, Move } from 'lucide-react';
// CDN-based Three.js Integration
import * as THREE from 'https://esm.sh/three';
import { OrbitControls } from 'https://esm.sh/three/examples/jsm/controls/OrbitControls';

const ThreeEngine = ({ pilotMode, activeInstrument, flux, playbackProgress, jitter, glowOpacity }) => {
    const mountRef = useRef(null);
    const cameraRef = useRef(null);
    const controlsRef = useRef(null);
    const chassisRef = useRef(null);
    const particleRef = useRef(null);
    const glowMaterialRef = useRef(null);

    const instrumentPositions = useMemo(() => ({
        DEFAULT: { x: 0, y: 0, z: 25 },
        VELC: { x: 0, y: 3, z: 12 },
        SUIT: { x: 2, y: 1, z: 14 },
        SoLEXS: { x: -2, y: 1, z: 14 },
        MAG: { x: 0, y: -4, z: 15 },
        ASPEX: { x: 3, y: 0, z: 12 },
        PAPA: { x: -3, y: 0, z: 12 },
        HEL1OS: { x: 0, y: 0, z: 10 }
    }), []);

    useEffect(() => {
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        cameraRef.current = camera;
        
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        mountRef.current.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.enabled = false; 
        controlsRef.current = controls;

        const starGeo = new THREE.BufferGeometry();
        const starPos = new Float32Array(6000 * 3);
        for(let i=0; i<18000; i++) starPos[i] = (Math.random() - 0.5) * 800;
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
        scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({color: 0xffffff, size: 0.1})));

        const sun = new THREE.Mesh(new THREE.SphereGeometry(6, 64, 64), new THREE.MeshBasicMaterial({ color: 0xffff44 }));
        sun.position.set(-50, 20, -100);
        scene.add(sun);
        scene.add(new THREE.PointLight(0xffffff, 3, 300));

        const chassis = new THREE.Group();
        const body = new THREE.Mesh(new THREE.BoxGeometry(2, 2, 2), new THREE.MeshStandardMaterial({ color: 0x444444, metalness: 0.9, roughness: 0.2 }));
        
        const glowMat = new THREE.MeshBasicMaterial({ color: 0x00ffff, transparent: true, opacity: 0.5 });
        glowMaterialRef.current = glowMat;
        const glowMesh = new THREE.Mesh(new THREE.BoxGeometry(2.1, 2.1, 2.1), glowMat);
        chassis.add(body, glowMesh);

        const panelMat = new THREE.MeshStandardMaterial({ color: 0x002244 });
        const pL = new THREE.Mesh(new THREE.BoxGeometry(6, 0.1, 2), panelMat); pL.position.x = -4;
        const pR = new THREE.Mesh(new THREE.BoxGeometry(6, 0.1, 2), panelMat); pR.position.x = 4;
        chassis.add(pL, pR);

        scene.add(chassis);
        chassisRef.current = chassis;

        const pGeo = new THREE.BufferGeometry();
        const pPos = new Float32Array(2000 * 3);
        const pVel = new Float32Array(2000);
        for(let i=0; i<2000; i++) {
            pPos[i*3] = (Math.random()-0.5)*20;
            pPos[i*3+1] = (Math.random()-0.5)*20;
            pPos[i*3+2] = (Math.random()-0.5)*10;
            pVel[i] = 0.1 + Math.random()*0.2;
        }
        pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
        const particles = new THREE.Points(pGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.05, transparent: true, opacity: 0.4 }));
        scene.add(particles);
        particleRef.current = { geo: pGeo, vel: pVel };

        camera.position.z = 25;

        const animate = () => {
            requestAnimationFrame(animate);
            
            if (!controls.enabled) {
                const target = instrumentPositions[activeInstrument] || instrumentPositions.DEFAULT;
                
                // Fly-to with Jitter integration for magnetic instability
                const jitterX = (Math.random() - 0.5) * jitter;
                const jitterY = (Math.random() - 0.5) * jitter;
                const jitterZ = (Math.random() - 0.5) * jitter;
                
                camera.position.lerp(new THREE.Vector3(target.x + jitterX, target.y + jitterY, target.z + jitterZ), 0.05);
                camera.lookAt(chassis.position);
            } else {
                controls.update();
            }

            // High-Glow Feedback based on MAG_max
            if (glowMaterialRef.current) {
                glowMaterialRef.current.opacity = glowOpacity;
                glowMaterialRef.current.color.setHSL(0.5 - glowOpacity * 0.5, 1, 0.5);
            }

            if (chassisRef.current) {
                chassisRef.current.rotation.y += 0.005 + (jitter * 0.1);
            }

            // Particle Flux sync
            const positions = pGeo.attributes.position.array;
            for(let i=0; i<2000; i++) {
                positions[i*3+2] += pVel[i] * (1 + (flux / 2000));
                if(positions[i*3+2] > 40) positions[i*3+2] = -10;
            }
            pGeo.attributes.position.needsUpdate = true;

            renderer.render(scene, camera);
        };
        animate();

        const handleResize = () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        };
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            mountRef.current?.removeChild(renderer.domElement);
        };
    }, [activeInstrument, instrumentPositions, flux, jitter, glowOpacity]);

    useEffect(() => {
        if (controlsRef.current) {
            controlsRef.current.enabled = pilotMode;
        }
    }, [pilotMode]);

    return <div ref={mountRef} className="absolute inset-0 z-0" />;
};

    useEffect(() => {
        if (controlsRef.current) {
            controlsRef.current.enabled = pilotMode;
        }
    }, [pilotMode]);

    return <div ref={mountRef} className="absolute inset-0 z-0" />;
};

const PilotDashboard = () => {
    const [pilotMode, setPilotMode] = useState(false);
    const [activeInstrument, setActiveInstrument] = useState('DEFAULT');
    const [playbackProgress, setPlaybackProgress] = useState(0); // 0 to 1
    const [missionData, setMissionData] = useState([]);
    const [importance, setImportance] = useState({});
    
    // Fetch Integrated Data from Mission API
    useEffect(() => {
        const loadData = async () => {
            try {
                const [apiRes, importanceRes] = await Promise.all([
                    fetch('/public/mission_api_payload.json'),
                    fetch('/public/importance_manifest.json')
                ]);
                const data = await apiRes.json();
                const imp = await importanceRes.json();
                setMissionData(data);
                setImportance(imp);
            } catch (e) {
                console.warn("⚠️ Mission API not active. Using simulated stream.");
            }
        };
        loadData();
    }, []);

    // 10s-Sync Row Selection
    const currentFrame = useMemo(() => {
        if (!missionData.length) return null;
        const index = Math.floor(playbackProgress * (missionData.length - 1));
        return missionData[index];
    }, [playbackProgress, missionData]);

    const isRedAlert = currentFrame?.is_red_alert || false;

    // Adaptive Visual Parameters
    const currentVisuals = useMemo(() => {
        if (!currentFrame) return { flux: 500, jitter: 0, glow: 0.5 };
        
        const std = currentFrame.MAG_B_z_std || 0;
        const max = currentFrame.MAG_B_z_max || 0;
        
        return {
            flux: currentFrame.ASPEX_proton_count_mean || 500,
            jitter: isRedAlert ? 0.8 : Math.min(std * 0.2, 1.0),
            glow: isRedAlert ? 1.0 : Math.min(Math.abs(max) / 30, 1.0)
        };
    }, [currentFrame, isRedAlert]);

    return (
        <div className={`fixed inset-0 bg-slate-950 text-slate-100 flex overflow-hidden font-sans transition-colors duration-500 ${isRedAlert ? 'ring-inset ring-8 ring-red-900/40' : ''}`}>
            {/* Three.js Layer */}
            <ThreeEngine 
                pilotMode={pilotMode} 
                activeInstrument={activeInstrument} 
                flux={currentVisuals.flux}
                playbackProgress={playbackProgress}
                jitter={currentVisuals.jitter}
                glowOpacity={currentVisuals.glow}
            />

            {/* HUD Overlay - Glassmorphic */}
            <div className="absolute inset-0 z-10 pointer-events-none p-6 flex flex-col justify-between">
                
                <header className="flex justify-between items-start pointer-events-auto">
                    <div className="bg-slate-900/40 backdrop-blur-2xl border border-white/10 p-5 rounded-3xl shadow-2xl w-96">
                        <div className="flex items-center gap-3 mb-4">
                            <Radio className={`text-blue-400 ${isRedAlert ? 'text-red-500 animate-ping' : 'animate-pulse'}`} size={24} />
                            <h1 className={`text-lg font-bold tracking-tight ${isRedAlert ? 'text-red-400' : ''}`}>ADITYA-L1 COMMAND</h1>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-xs font-mono opacity-60">
                            <div>TIMESTAMP: <span className="text-blue-300">{currentFrame?.timestamp || 'SYNC_INITIALIZING'}</span></div>
                            <div>VELCITY: <span className="text-cyan-300">{(currentFrame?.VELC_velc_velocity_mean || 0).toFixed(2)} km/s</span></div>
                        </div>
                    </div>

                    <div className={`bg-slate-900/40 backdrop-blur-2xl border border-white/10 p-4 rounded-3xl flex items-center gap-4 shadow-2xl transition-all ${isRedAlert ? 'bg-red-950/40 border-red-500/50' : ''}`}>
                        <button 
                            className={`flex items-center gap-2 px-6 py-3 rounded-2xl transition-all ${pilotMode ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50' : 'bg-white/5 text-slate-400 hover:bg-white/10'}`}
                            onClick={() => setPilotMode(!pilotMode)}
                        >
                            <Move size={18} />
                            <span className="font-bold uppercase tracking-wider text-xs">Explore Mode</span>
                        </button>
                        <div className="h-8 w-px bg-white/10"></div>
                        <div className="flex flex-col items-center px-4">
                            <span className="text-[9px] text-slate-500 mb-1 uppercase tracking-tighter">Mission State</span>
                            <span className={`text-sm font-black ${isRedAlert ? 'text-red-500 animate-pulse' : 'text-green-400'}`}>
                                {isRedAlert ? 'RED_ALERT: CME_PREDICTED' : (currentFrame?.hours_to_event > 0 ? 'NOMINAL' : 'CME_ENGAGED')}
                            </span>
                        </div>
                    </div>
                </header>

                <footer className="flex justify-between items-end pointer-events-auto">
                    <div className={`bg-slate-900/40 backdrop-blur-2xl border border-white/10 p-6 rounded-3xl w-[450px] shadow-2xl ${isRedAlert ? 'border-red-500/30' : ''}`}>
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                                <Zap className={isRedAlert ? 'text-red-500 animate-bounce' : 'text-yellow-400'} size={18} />
                                <h2 className="text-xs font-bold uppercase tracking-widest text-slate-300">TFT Prognosis Time Machine</h2>
                            </div>
                            <span className="text-[10px] font-mono text-blue-400">
                                {isRedAlert && currentFrame?.predicted_shock_eta 
                                    ? `SHOCK_ETA: ${currentFrame.predicted_shock_eta.toFixed(1)}H`
                                    : `MISSION_T+${(playbackProgress * 168).toFixed(1)}H`}
                            </span>
                        </div>
                        
                        <input 
                            type="range" 
                            min="0" max="1" step="0.001" 
                            value={playbackProgress}
                            onChange={(e) => setPlaybackProgress(parseFloat(e.target.value))}
                            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
                        />
                        
                        <div className="flex justify-between mt-4 text-[10px] font-mono text-slate-500">
                            <span>QUIET_SUN (A)</span>
                            <span className="text-red-400">CAMPAIGN_PEAK (B)</span>
                        </div>
                    </div>

                    <div className="flex gap-4">
                        <button className="bg-slate-900/60 backdrop-blur-xl border border-white/5 px-8 py-4 rounded-3xl flex items-center gap-3 hover:bg-blue-600/20 transition-all group">
                             <Command size={20} className="text-cyan-400 group-hover:rotate-90 transition-transform" />
                             <span className="font-black uppercase tracking-widest text-xs">Prognosis Weights</span>
                        </button>
                    </div>
                </footer>
            </div>

            {/* Sidebar: Hybrid Instrument Selectors */}
            <aside className="w-80 h-full border-r border-white/5 bg-slate-950/80 backdrop-blur-3xl p-6 z-20 flex flex-col gap-6">
                <div className="flex items-center gap-2 mb-2">
                    <Database className="text-blue-400" size={20} />
                    <h2 className="text-lg font-bold">Payload Manifest</h2>
                </div>
                <div className="space-y-3 flex-1 overflow-y-auto pr-2 custom-scrollbar border-t border-white/5 pt-4">
                    {['MAG', 'ASPEX', 'VELC', 'SUIT', 'SoLEXS', 'HEL1OS', 'PAPA'].map((name) => (
                        <div 
                            key={name} 
                            onClick={() => {
                                setActiveInstrument(name);
                                setPilotMode(false);
                            }}
                            className={`p-4 rounded-2xl border transition-all cursor-pointer group flex justify-between items-center ${activeInstrument === name ? 'bg-blue-600/20 border-blue-500/50 shadow-lg shadow-blue-500/10' : 'bg-white/5 border-white/5 hover:border-white/20'}`}
                        >
                            <span className={`text-xs font-bold uppercase tracking-wider ${activeInstrument === name ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'}`}>{name}</span>
                            <div className="flex items-center gap-2">
                                <span className={`w-1.5 h-1.5 rounded-full ${instrumentStatuses[name] === 'CRITICAL_SENSING' ? 'bg-red-500 animate-ping' : 'bg-green-500'}`}></span>
                                <span className="text-[9px] font-mono text-slate-500">{instrumentStatuses[name] || 'NOMINAL'}</span>
                            </div>
                        </div>
                    ))}
                    <div 
                        onClick={() => setActiveInstrument('DEFAULT')}
                        className={`p-4 rounded-2xl border transition-all cursor-pointer text-center text-[10px] font-black tracking-widest mt-6 ${activeInstrument === 'DEFAULT' ? 'bg-slate-800 border-white/20' : 'bg-white/5 border-transparent opacity-40'}`}
                    >
                        RESET_VIEWPORT
                    </div>
                </div>
                <div className="pt-6 border-t border-white/5">
                    <p className="text-[9px] text-slate-500 text-center uppercase tracking-widest leading-relaxed">Integrated Data Pipeline<br/>BrahmaTron Edge v1.0.Decimate</p>
                </div>
            </aside>
        </div>
    );
};

export default PilotDashboard;
