import React from "react"
import clsx from "clsx"
import styles from "./styles.module.css"

const FeatureList = [
  {
    title: "Easy to Use",
    Svg: require("@site/static/img/undraw_docusaurus_mountain.svg").default,
    description: (
      <>
        Dispatch was designed to stay out of the spotlight, instead opting to supercharge existing
        tools (Slack, Google Docs, etc.,) for us in incident response.
      </>
    ),
  },
  {
    title: "Focus on What Matters",
    Svg: require("@site/static/img/undraw_docusaurus_tree.svg").default,
    description: (
      <>
        Dispatch lets you focus on your incident, let Dispatch manage timelines, documentation and
        people leaving you to focus on resolve the incident.
      </>
    ),
  },
  {
    title: "API First",
    Svg: require("@site/static/img/undraw_docusaurus_react.svg").default,
    description: <>Extend or customize Dispatch via it's API or integrated plugins.</>,
  },
]

function Feature({ Svg, title, description }) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  )
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  )
}
