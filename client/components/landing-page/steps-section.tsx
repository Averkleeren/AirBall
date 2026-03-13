const steps = [
  {
    number: "01",
    title: "Upload your video",
    description: "Record yourself shooting and upload the clip. Any angle works.",
  },
  {
    number: "02",
    title: "AI analyzes your shot",
    description:
      "Our model tracks the ball, your body mechanics, and the shot trajectory frame by frame.",
  },
  {
    number: "03",
    title: "Get your stats",
    description:
      "See your shot score, arc angle, release speed, and follow-through rating instantly.",
  },
]

export function StepsSection() {
  return (
    <section className="border-t border-border bg-secondary/50 px-6 py-32">
      <div className="mx-auto max-w-6xl">
        <div className="mb-16 text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-primary">
            How it works
          </p>
          <h2 className="text-balance text-3xl font-bold tracking-tight text-foreground md:text-4xl">
            Three steps to a better shot
          </h2>
        </div>

        <div className="grid gap-12 md:grid-cols-3">
          {steps.map((step) => (
            <div key={step.number} className="text-center">
              <span className="mb-4 inline-block font-mono text-4xl font-bold text-primary/30">
                {step.number}
              </span>
              <h3 className="mb-2 text-lg font-semibold text-foreground">
                {step.title}
              </h3>
              <p className="leading-relaxed text-muted-foreground">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
