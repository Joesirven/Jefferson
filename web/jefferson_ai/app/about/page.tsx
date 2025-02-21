export default function DemoPage() {
    return (
      <div className="w-screen h-screen bg-black flex items-center justify-center">
        <video
          controls
          className="w-full h-full object-contain"
          playsInline
          preload="auto"
          autoPlay
        >
          <source src="/videos/demo.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>
    );
  }
