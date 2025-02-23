// it has the video and nothing else; only controls to play and pause
// which usually come with the built in video player

export default function AboutPage() {
  return (
    <div className="w-screen h-screen bg-black flex items-center justify-center">

        <video
        controls
        className="w-full h-full object-contain"
        playsInline
        preload="auto"
        autoPlay
        >
            <source src="/videos/about.mov" type="video/mov" />
            Your browser does not support the video tag.
        </video>
    </div>
  );
}
